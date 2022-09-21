use std::{collections::HashMap, process::Command};

use anyhow::{Error, Result};
use clap::{ArgEnum, Args, Parser, Subcommand};
use nix::mount::{mount, MsFlags};

#[derive(Parser)]
#[clap(author, version, about, long_about = None)]
#[clap(propagate_version = true)]
struct Cli {
    #[clap(arg_enum, short, long, default_value_t = LogLevel::Info)]
    log_level: LogLevel,

    #[clap(subcommand)]
    command: Commands,
}

#[derive(Copy, Clone, PartialEq, Eq, PartialOrd, Ord, ArgEnum)]
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
    Check(CheckArguments),
    SetCounter(SetCounterArguments),
    Success(SuccessArguments),
}

#[derive(Args)]
struct CheckArguments {}

#[derive(Args)]
struct SetCounterArguments {}

#[derive(Args)]
struct SuccessArguments {}

fn check(_args: &CheckArguments) -> Result<(), Error> {
    let grub2_editenv_list = parse_grub2_editenv_list()?;
    if let Some(v) = grub2_editenv_list.get("boot_counter") {
        if v == "1" {
            Command::new("rpm-ostree").arg("rollback").spawn()?;
            Command::new("grub2-editenv")
                .arg("-")
                .arg("unset")
                .arg("boot_counter")
                .spawn()?;
        }
    }
    Ok(())
}

fn set_counter(_args: &SetCounterArguments) -> Result<(), Error> {
    Ok(())
}

fn success(_args: &SuccessArguments) -> Result<(), Error> {
    Ok(())
}

fn parse_grub2_editenv_list() -> Result<HashMap<String, String>> {
    let output = Command::new("grub2-editenv").arg("list").output()?;
    let stdout = String::from_utf8(output.stdout)?;
    let split = stdout.split('\n').collect::<Vec<&str>>();
    let mut hm = HashMap::new();
    for s in split {
        if s.len() == 0 {
            continue;
        }
        let ss = s.split('=').collect::<Vec<&str>>();
        if ss.len() != 2 {
            continue;
        }
        hm.insert(ss[0].to_string(), ss[1].to_string());
    }
    Ok(hm)
}

fn main() -> Result<()> {
    let cli = Cli::parse();

    pretty_env_logger::formatted_builder()
        .filter_level(cli.log_level.to_log())
        .init();

    mount::<str, str, str, str>(None, "/boot", None, MsFlags::MS_REMOUNT, None)?;

    match cli.command {
        Commands::Check(args) => check(&args),
        Commands::SetCounter(args) => set_counter(&args),
        Commands::Success(args) => success(&args),
    }
}
