/// This module contains most of the low-level commands
/// and grub variable modifications
use anyhow::{bail, Result};

use std::process::Command;
use std::str;

/// reboots the system if boot_counter is greater than 0 or can be forced too
pub fn handle_reboot(force: bool) -> Result<()> {
    if !force {
        if let Some(t) = get_boot_counter()? {
            if t <= 0 {
                bail!("countdown ended, check greenboot-rollback status")
            };
        }
    }
    log::info!("restarting the system");
    Command::new("systemctl").arg("reboot").status()?;
    Ok(())
}

/// rollback to previous ostree deployment if boot counter is less than 0
pub fn handle_rollback() -> Result<()> {
    if let Some(boot_counter) = get_boot_counter()? {
        if boot_counter <= 0 {
            log::info!("Greenboot will now attempt to rollback");
            Command::new("rpm-ostree").arg("rollback").status()?;
            return Ok(());
        }
    }
    bail!("Rollback not initiated");
}

/// sets grub variable boot_counter if not set
pub fn set_boot_counter(reboot_count: i32) -> Result<()> {
    match get_boot_counter() {
        Ok(Some(current_counter)) => {
            log::info!("boot_counter={current_counter}");
            bail!("counter already set");
        }
        _ => {
            //will still try to set boot_counter to override cases like boot_counter=<some_string>
            log::info!("setting boot counter");
            set_grub_var("boot_counter", reboot_count)?;
        }
    }
    Ok(())
}

/// resets grub variable boot_counter
pub fn unset_boot_counter() -> Result<()> {
    Command::new("grub2-editenv")
        .arg("-")
        .arg("unset")
        .arg("boot_counter")
        .status()?;
    Ok(())
}

/// sets grub variable boot_success
pub fn set_boot_status(success: bool) -> Result<()> {
    if success {
        set_grub_var("boot_success", 1)?;
        unset_boot_counter()?;
    } else {
        set_grub_var("boot_success", 0)?;
    }
    Ok(())
}

/// writes greenboot status to motd.d/boot-status
pub fn handle_motd(state: &str) -> Result<()> {
    std::fs::write(
        "/etc/motd.d/boot-status",
        format!("Greenboot {state}.").as_bytes(),
    )?;
    Ok(())
}

/// fetches boot_counter value, none if not set
pub fn get_boot_counter() -> Result<Option<i32>> {
    let grub_vars = Command::new("grub2-editenv")
        .arg("-")
        .arg("list")
        .output()?;
    let grub_vars = str::from_utf8(&grub_vars.stdout[..])?;
    for var in grub_vars.lines() {
        let (k, v) = if let Some(kv) = var.split_once('=') {
            kv
        } else {
            continue;
        };
        if k != "boot_counter" {
            continue;
        }

        let counter_value = v.parse::<i32>()?;
        return Ok(Some(counter_value));
    }
    Ok(None)
}

/// helper function to set any grub variable
fn set_grub_var(key: &str, val: i32) -> Result<()> {
    Command::new("grub2-editenv")
        .arg("-")
        .arg("set")
        .arg(format!("{key}={val}"))
        .status()?;
    Ok(())
}
