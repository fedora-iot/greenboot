mod handler;
use anyhow::{bail, Result};
use clap::{Parser, Subcommand, ValueEnum};
use config::{Config, File, FileFormat};
use glob::glob;
use handler::*;
use serde::Deserialize;
use std::error::Error;
use std::path::Path;
use std::process::Command;
use std::str;

/// dir that greenboot looks for the health check and other scripts
static GREENBOOT_INSTALL_PATHS: [&str; 2] = ["/usr/lib/greenboot", "/etc/greenboot"];

/// greenboot config path
static GREENBOOT_CONFIG_FILE: &str = "/etc/greenboot/greenboot.conf";

#[derive(Parser)]
#[clap(author, version, about, long_about = None)]
#[clap(propagate_version = true)]
/// cli parameters for greenboot
struct Cli {
    #[clap(value_enum, short, long, default_value_t = LogLevel::Info)]
    log_level: LogLevel,
    #[clap(subcommand)]
    command: Commands,
}
#[derive(Debug, Deserialize)]
/// config params for greenboot
struct GreenbootConfig {
    max_reboot: u16,
}

impl GreenbootConfig {
    /// sets the default parameter for greenboot config
    fn set_default() -> Self {
        Self { max_reboot: 3 }
    }
    /// gets the config from the config file
    fn get_config() -> Self {
        let mut config = Self::set_default();
        let parsed = Config::builder()
            .add_source(File::new(GREENBOOT_CONFIG_FILE, FileFormat::Ini))
            .build();
        match parsed {
            Ok(c) => {
                config.max_reboot = match c.get_int("GREENBOOT_MAX_BOOT_ATTEMPTS") {
                    Ok(c) => c.try_into().unwrap_or_else(|e| {
                        log::warn!(
                            "{e}, config error, using default value: {}",
                            config.max_reboot
                        );
                        config.max_reboot
                    }),
                    Err(e) => {
                        log::warn!(
                            "{e}, config error, using default value: {}",
                            config.max_reboot
                        );
                        config.max_reboot
                    }
                }
            }
            Err(e) => log::warn!(
                "{e}, config error, using default value: {}",
                config.max_reboot
            ),
        }
        config
    }
}

#[derive(Copy, Clone, PartialEq, Eq, PartialOrd, Ord, ValueEnum)]
/// log level for journald logging
enum LogLevel {
    Trace,
    Debug,
    Info,
    Warn,
    Error,
    Off,
}

impl LogLevel {
    fn to_log(self) -> log::LevelFilter {
        match self {
            LogLevel::Trace => log::LevelFilter::Trace,
            LogLevel::Debug => log::LevelFilter::Debug,
            LogLevel::Info => log::LevelFilter::Info,
            LogLevel::Warn => log::LevelFilter::Warn,
            LogLevel::Error => log::LevelFilter::Error,
            LogLevel::Off => log::LevelFilter::Off,
        }
    }
}

#[derive(Subcommand)]
/// params that greenboot accepts
///
/// greenboot health-check -> runs the custom health checks
///
/// greenboot rollback -> if boot_counter satisfies it trigger rollback
enum Commands {
    HealthCheck,
    Rollback,
}

/// runs all the scripts in required.d and wanted.d
fn run_diagnostics() -> Result<()> {
    let mut required_script_failure: bool = false;
    let mut path_exists: bool = false;
    for path in GREENBOOT_INSTALL_PATHS {
        let greenboot_required_path = format!("{path}/check/required.d/");
        if !Path::new(&greenboot_required_path).is_dir() {
            log::warn!("skipping test as {greenboot_required_path} is not a dir");
            continue;
        }
        path_exists = true;
        let errors = run_scripts("required", &greenboot_required_path);
        if !errors.is_empty() {
            log::error!("required script error:");
            errors.iter().for_each(|e| log::error!("{e}"));
            if !required_script_failure {
                required_script_failure = true;
            }
        }
    }
    if !path_exists {
        bail!("cannot find any required.d folder");
    }
    for path in GREENBOOT_INSTALL_PATHS {
        let greenboot_wanted_path = format!("{path}/check/wanted.d/");
        let errors = run_scripts("wanted", &greenboot_wanted_path);
        if !errors.is_empty() {
            log::warn!("wanted script runner error:");
            errors.iter().for_each(|e| log::error!("{e}"));
        }
    }

    if required_script_failure {
        bail!("health-check failed!");
    }
    Ok(())
}

/// runs all the scripts in red.d when health-check fails
fn run_red() -> Vec<Box<dyn Error>> {
    let mut errors = Vec::new();
    for path in GREENBOOT_INSTALL_PATHS {
        let red_path = format!("{path}/red.d/");
        let e = run_scripts("red", &red_path);
        if !e.is_empty() {
            errors.extend(e);
        }
    }
    errors
}

/// runs all the scripts green.d when health-check passes
fn run_green() -> Vec<Box<dyn Error>> {
    let mut errors = Vec::new();
    for path in GREENBOOT_INSTALL_PATHS {
        let green_path = format!("{path}/green.d/");
        let e = run_scripts("green", &green_path);
        if !e.is_empty() {
            errors.extend(e);
        }
    }
    errors
}

/// triggers the diagnostics followed by the action on the outcome
/// this also handles setting the grub variables and system restart
fn health_check() -> Result<()> {
    let config = GreenbootConfig::get_config();
    log::debug!("{config:?}");
    handle_motd("healthcheck is in progress")?;
    match run_diagnostics() {
        Ok(()) => {
            log::info!("greenboot health-check passed.");
            let errors = run_green();
            if !errors.is_empty() {
                log::error!("There is a problem with green script runner");
                errors.iter().for_each(|e| log::error!("{e}"));
            }
            handle_motd("healthcheck passed - status is GREEN")
                .unwrap_or_else(|e| log::error!("cannot set motd: {}", e.to_string()));
            set_boot_status(true)?;
            Ok(())
        }
        Err(e) => {
            log::error!("Greenboot error: {e}");
            handle_motd("healthcheck failed - status is RED")
                .unwrap_or_else(|e| log::error!("cannot set motd: {}", e.to_string()));
            let errors = run_red();
            if !errors.is_empty() {
                log::error!("There is a problem with red script runner");
                errors.iter().for_each(|e| log::error!("{e}"));
            }

            set_boot_status(false)?;
            set_boot_counter(config.max_reboot)
                .unwrap_or_else(|e| log::error!("cannot set boot_counter: {}", e.to_string()));
            handle_reboot(false)
                .unwrap_or_else(|e| log::error!("cannot reboot: {}", e.to_string()));
            Err(e)
        }
    }
}

/// initiates rollback if boot_counter and satisfies
fn trigger_rollback() -> Result<()> {
    match handle_rollback() {
        Ok(()) => {
            log::info!("Rollback successful");
            unset_boot_counter()?;
            handle_reboot(true)
        }
        Err(e) => {
            bail!("{e}, Rollback is not initiated");
        }
    }
}

/// takes in a path and runs all the .sh files within the path
/// returns false if any script fails
fn run_scripts(name: &str, path: &str) -> Vec<Box<dyn Error>> {
    let mut errors = Vec::new();
    let scripts = format!("{path}*.sh");
    match glob(&scripts) {
        Ok(s) => {
            for entry in s.flatten() {
                log::info!("running {name} check {}", entry.to_string_lossy());
                let output = Command::new("bash").arg("-C").arg(entry.clone()).output();
                match output {
                    Ok(o) => {
                        if !o.status.success() {
                            errors.push(Box::new(std::io::Error::new(
                                std::io::ErrorKind::Other,
                                format!(
                                    "{name} script {} failed! \n{} \n{}",
                                    entry.to_string_lossy(),
                                    String::from_utf8_lossy(&o.stdout),
                                    String::from_utf8_lossy(&o.stderr)
                                ),
                            )) as Box<dyn Error>);
                        } else {
                            log::info!("{name} script {} success!", entry.to_string_lossy());
                        }
                    }
                    Err(e) => {
                        errors.push(Box::new(e) as Box<dyn Error>);
                    }
                }
            }
        }
        Err(e) => errors.push(Box::new(e) as Box<dyn Error>),
    }
    errors
}

fn main() -> Result<()> {
    let cli = Cli::parse();
    pretty_env_logger::formatted_builder()
        .filter_level(cli.log_level.to_log())
        .init();

    match cli.command {
        Commands::HealthCheck => health_check(),
        Commands::Rollback => trigger_rollback(),
    }
}

#[cfg(test)]
mod tests {
    use std::fs;

    use anyhow::Context;

    use super::*;

    /// validate when the required folder is not found
    #[test]
    fn missing_required_folder() {
        assert_eq!(
            run_diagnostics().unwrap_err().to_string(),
            String::from("cannot find any required.d folder")
        );
    }

    #[test]
    fn test_passed_diagnostics() {
        setup_folder_structure(true)
            .context("Test setup failed")
            .unwrap();
        let state = run_diagnostics();
        assert!(state.is_ok());
        tear_down().context("Test teardown failed").unwrap();
    }

    #[test]
    fn test_failed_diagnostics() {
        setup_folder_structure(false)
            .context("Test setup failed")
            .unwrap();
        let failed_msg = run_diagnostics().unwrap_err().to_string();
        assert_eq!(failed_msg, String::from("health-check failed!"));
        tear_down().context("Test teardown failed").unwrap();
    }

    #[test]
    fn test_boot_counter_set() {
        unset_boot_counter().ok();
        set_boot_counter(10).ok();
        assert_eq!(get_boot_counter().unwrap(), Some(10));
        unset_boot_counter().ok();
    }

    #[test]
    fn test_boot_counter_re_set() {
        unset_boot_counter().ok();
        set_boot_counter(10).ok();
        set_boot_counter(20).ok();
        assert_eq!(get_boot_counter().unwrap(), Some(10));
        unset_boot_counter().ok();
    }

    #[test]
    fn test_boot_counter_having_invalid_value() {
        unset_boot_counter().ok();
        let _ = Command::new("grub2-editenv")
            .arg("-")
            .arg("set")
            .arg("boot_counter=foo")
            .spawn()
            .context("Cannot create grub variable boot_counter");
        set_boot_counter(13).ok();
        assert_eq!(get_boot_counter().unwrap(), Some(13));
        unset_boot_counter().ok();
    }

    fn setup_folder_structure(passing: bool) -> Result<()> {
        let required_path = format!("{}/check/required.d", GREENBOOT_INSTALL_PATHS[1]);
        let wanted_path = format!("{}/check/wanted.d", GREENBOOT_INSTALL_PATHS[1]);
        let passing_test_scripts = "testing_assets/passing_script.sh";
        let failing_test_scripts = "testing_assets/failing_script.sh";

        fs::create_dir_all(&required_path).expect("cannot create folder");
        fs::create_dir_all(&wanted_path).expect("cannot create folder");
        let _a = fs::copy(
            passing_test_scripts,
            format!("{}/passing_script.sh", &required_path),
        )
        .context("unable to copy test assets");

        let _a = fs::copy(
            passing_test_scripts,
            format!("{}/passing_script.sh", &wanted_path),
        )
        .context("unable to copy test assets");

        let _a = fs::copy(
            failing_test_scripts,
            format!("{}/failing_script.sh", &wanted_path),
        )
        .context("unable to copy test assets");

        if !passing {
            let _a = fs::copy(
                failing_test_scripts,
                format!("{}/failing_script.sh", &required_path),
            )
            .context("unable to copy test assets");
            return Ok(());
        }
        Ok(())
    }

    fn tear_down() -> Result<()> {
        fs::remove_dir_all(GREENBOOT_INSTALL_PATHS[1]).expect("Unable to delete folder");
        Ok(())
    }
}
