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
    Ok(())
}

fn set_counter(_args: &SetCounterArguments) -> Result<(), Error> {
    Ok(())
}

fn success(_args: &SuccessArguments) -> Result<(), Error> {
    Ok(())
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
