/// This module contains most of the low-level commands
/// and grub variable modifications
use anyhow::{bail, Result};
use std::process::Command;
use std::str;

/// reboots the system if boot_counter is greater than 0 or can be forced too
pub fn handle_reboot(force: bool) -> Result<()> {
    if !force {
        match get_boot_counter() {
            Some(t) => {
                if t <= 0 {
                    bail!("countdown ended, check greenboot-rollback status")
                }
            }
            None => bail!("boot_counter is not set"),
        }
    }
    log::info!("restarting system");
    let status = Command::new("systemctl").arg("reboot").status()?;
    if status.success() {
        return Ok(());
    }
    bail!("systemd returned error");
}

/// rollback to previous ostree deployment if boot counter is less than 0
pub fn handle_rollback() -> Result<()> {
    if let Some(t) = get_boot_counter() {
        if t <= 0 {
            log::info!("Greenboot will now attempt to rollback");
            let status = Command::new("rpm-ostree").arg("rollback").status()?;
            if status.success() {
                return Ok(());
            }
            bail!(status.to_string());
        }
    }
    log::info!("Rollback not initiated as boot_counter is either unset or not equal to 0");
    Ok(())
}

/// sets grub variable boot_counter if not set
pub fn set_boot_counter(reboot_count: i32) -> Result<()> {
    if let Some(current_counter) = get_boot_counter() {
        log::info!("boot_counter={current_counter}");
        return Ok(());
    } else if set_grub_var("boot_counter", reboot_count) {
        log::info!("Set boot_counter={reboot_count}");
        return Ok(());
    }
    bail!("Failed to set GRUB variable: boot_counter");
}

/// resets grub variable boot_counter
pub fn unset_boot_counter() -> Result<()> {
    let status = Command::new("grub2-editenv")
        .arg("-")
        .arg("unset")
        .arg("boot_counter")
        .status()?;
    if status.success() {
        return Ok(());
    }
    bail!("grub returned an error")
}

/// sets grub variable boot_success
pub fn handle_boot_success(success: bool) -> Result<()> {
    if success {
        if !set_grub_var("boot_success", 1) {
            bail!("unable to mark boot as success, grub returned an error")
        }
        match unset_boot_counter() {
            Ok(_) => return Ok(()),
            Err(e) => bail!("unable to remove boot_counter, {e}"),
        }
    } else if !set_grub_var("boot_success", 0) {
        bail!("unable to mark boot as failure, grub returned an error")
    }
    Ok(())
}

/// writes greenboot status to motd.d/boot-status
pub fn handle_motd(state: &str) -> Result<()> {
    let motd = format!("Greenboot {state}.");

    std::fs::write("/etc/motd.d/boot-status", motd.as_bytes())?;
    Ok(())
}

/// fetches boot_counter value, none if not set
pub fn get_boot_counter() -> Option<i32> {
    let grub_vars = Command::new("grub2-editenv").arg("-").arg("list").output();
    if grub_vars.is_err() {
        return None;
    }
    let grub_vars = grub_vars.unwrap();
    let grub_vars = match str::from_utf8(&grub_vars.stdout[..]) {
        Ok(vars) => vars.lines(),
        Err(e) => {
            log::error!("Unable to fetch grub variables, {e}");
            return None;
        }
    };

    for var in grub_vars {
        let (k, v) = if let Some(kv) = var.split_once('=') {
            kv
        } else {
            continue;
        };
        if k != "boot_counter" {
            continue;
        }
        match v.parse::<i32>() {
            Ok(count) => return Some(count),
            Err(_) => {
                log::error!("boot_counter not a valid integer");
                return None;
            }
        }
    }
    None
}

/// helper function to set any grub variable
fn set_grub_var(key: &str, val: i32) -> bool {
    match Command::new("grub2-editenv")
        .arg("-")
        .arg("set")
        .arg(format!("{key}={val}"))
        .status()
    {
        Ok(status) => {
            if status.success() {
                return true;
            }
            false
        }
        Err(_) => false,
    }
}
