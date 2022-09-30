use std::hash::Hash;
use std::io::ErrorKind;
use std::iter::FromIterator;
use std::{
    collections::HashSet,
    fs::{self, File},
    process::Command,
};

use anyhow::{bail, Error, Result};
use clap::{Parser, Subcommand, ValueEnum};
use glob::glob;
use serde::{Deserialize, Serialize};

#[derive(Parser)]
#[clap(author, version, about, long_about = None)]
#[clap(propagate_version = true)]
struct Cli {
    #[clap(value_enum, short, long, default_value_t = LogLevel::Info)]
    log_level: LogLevel,

    #[clap(subcommand)]
    command: Commands,
}

#[derive(Copy, Clone, PartialEq, Eq, PartialOrd, Ord, ValueEnum)]
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
enum Commands {
    Check,
    Stamp,
}

#[derive(Serialize, Deserialize, PartialEq, Eq, Hash)]
struct ServiceStatus {
    unit: String,
}

fn check() -> Result<(), Error> {
    match File::open("/etc/greenboot/upgrade.stamp") {
        Ok(_) => {
            log::info!("stamp on disk, removing and running greenboot");
            std::fs::remove_file("/etc/greenboot/upgrade.stamp")?
        }
        Err(e) => match e.kind() {
            ErrorKind::NotFound => return Ok(()),
            _ => {
                bail!("unknown error when opening stamp file: {:?}", e);
            }
        },
    }
    let mut failure = false;
    for path in [
        "/usr/lib/greenboot/check/required.d/*.sh",
        "/etc/greenboot/check/required.d/*.sh",
    ] {
        for entry in glob(path)?.flatten() {
            log::info!("running required check {}", entry.to_string_lossy());
            let output = Command::new("bash").arg("-C").arg(entry).output()?;
            if !output.status.success() {
                // combine and print stderr/stdout
                log::warn!("required script failed...");
                failure = true;
            }
        }
    }
    for path in [
        "/usr/lib/greenboot/check/wanted.d/*.sh",
        "/etc/greenboot/check/wanted.d/*.sh",
    ] {
        for entry in glob(path)?.flatten() {
            log::info!("running required check {}", entry.to_string_lossy());
            let output = Command::new("bash").arg("-C").arg(entry).output()?;
            if !output.status.success() {
                // combine and print stderr/stdout
                log::warn!("wanted script failed...");
            }
        }
    }
    // if a command with restart option in systemd fails to start we don't get it as "failed"
    // reversing the check makes sure that if by the time After=multi-user the service isn't running then it's failing at least
    let output = Command::new("systemctl")
        .arg("list-units")
        .arg("--state")
        .arg("active")
        .arg("--no-page")
        .arg("--output")
        .arg("json")
        .output()?;
    let services: Vec<ServiceStatus> = serde_json::from_str(&String::from_utf8(output.stdout)?)?;
    let ss: Vec<String> = services.iter().map(|x| x.unit.clone()).collect();
    let active_units: HashSet<String> = HashSet::from_iter(ss);
    for service in ["sshd.service", "NetworkManager.service"] {
        if !active_units.contains(service) {
            log::warn!("service {} failed, see journal", service);
            failure = true;
        }
    }
    if failure {
        for path in ["/etc/greenboot/red.d/*.sh"] {
            for entry in glob(path)?.flatten() {
                log::info!("running red check {}", entry.to_string_lossy());
                let output = Command::new("bash").arg("-C").arg(entry).output()?;
                if !output.status.success() {
                    // combine and print stderr/stdout
                    log::warn!("red script failed...");
                }
            }
        }
        log::warn!("SYSTEM is UNHEALTHY. Rolling back and rebooting...");
        Command::new("rpm-ostree").arg("rollback").status()?;
        reboot()?;
        return Ok(());
    }
    for path in ["/etc/greenboot/green.d/*.sh"] {
        for entry in glob(path)?.flatten() {
            log::info!("running green check {}", entry.to_string_lossy());
            let output = Command::new("bash").arg("-C").arg(entry).output()?;
            if !output.status.success() {
                // combine and print stderr/stdout
                log::warn!("green script failed...");
            }
        }
    }
    Ok(())
}

fn reboot() -> Result<(), Error> {
    Command::new("systemctl").arg("reboot").spawn()?;
    Ok(())
}

fn stamp() -> Result<(), Error> {
    fs::create_dir_all("/etc/greenboot/")?;
    File::create("/etc/greenboot/upgrade.stamp")?;
    Ok(())
}

fn main() -> Result<()> {
    let cli = Cli::parse();

    pretty_env_logger::formatted_builder()
        .filter_level(cli.log_level.to_log())
        .init();

    match cli.command {
        Commands::Check => check(),
        Commands::Stamp => stamp(),
    }
}
