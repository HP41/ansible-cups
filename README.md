# Ansible Role: cups

[![Build Status](https://travis-ci.org/HP41/ansible-cups.svg?branch=master)](https://travis-ci.org/HP41/ansible-cups)

## Installs CUPS, installs necessary PPDs and installs printers and classes on CUPS
### Install and configure CUPS
* Installs `cups` and `cups-pdf`
* Accounts defined in `cups_lpadmin_users` will be added to `lpadmin` group to administrate CUPS.
* Installs `cups-lpd` if variables allow (see below):
    * Creates a user account which will run the cups-lpd process.
    * Installs `xinetd` to run cups-lpd as a service. Uses the cups-lpd template file to create the final xinetd config.
* Configuring CUPS:
    * If templates for cupsd.conf, cups-browsed.conf and snmp.conf are provided they'll be built and copied over
    * If SSL certs are provided it'll copy them over to the proper location.

### Install PPDs
* Creates `/opt/share/ppd` where CUPS looks for PPDs that are manually copied over.
* Adds OpenPrinting Repo.
* Install Ricoh OpenPrinting Package - `openprinting-ppds-postscript-ricoh`
    * Also unzip the PPDs it installs as the package installs them as gzip files in `/opt/OpenPrinting-Ricoh/ppds/Ricoh`
* Installs HPLIP:
    * Also installs the HP proprietary plugin using an expect script.
* Copies over PPDs from the folder if specified in  `cups_ppd_files_to_be_copied` to `/opt/share/ppd`

### Install Printers
* Any printers defined to be removed will be removed first.
* Install Printers listed in the `cups_printer_list` variable and then installs classes listed in the `cups_class_list`
    * See [cups_printer_list and cups_class_list](tasks/printer_install.yml) to see how to define each printer and class object in the variable `cups_printer_list` and `cups_class_list` respectively.
    * This uses the [cups_lpadmin](library/cups_lpadmin.py) module. There's documentation/comments within it on how it can be used.
    * cups\_lpadmin is a direct copy from [HP41.ansible-modules-extra](https://github.com/HP41/ansible-modules-extras)/system/cups\_lpadmin. Once it's merged upstream, it'll be removed from here.

## Requirements
* Ansible >= 2.1
* Guest machine: Debian
    - stretch
    - jessie
    - wheezy
* Guest machine: Ubuntu
    - xenial
    - trusty
    - precise

## Possible additional tasks that are not part of this role's responsibilities.
* Opening the necessary CUPS ports - 515(LPR), 631(IPP/IPPS), 9100(direct IP) through the firewall.
    * If you'd like to use [debops.ferm](https://github.com/debops/ansible-ferm) you can use/modify `cups__debops_ferm_dependent_rules` (defined in defaults) to pass through to [debops.ferm](https://github.com/debops/ansible-ferm).

## Default Variables that can be overridden or used as-is when using this role:
### CUPS install and config:
* `cups_lpadmin_users`: List of users that must be added to cups admin (`lpadmin`) group. Default=root
* `cups_lpd`: Whether to install and setup cups-lpd - Default=`True`
* `cups_sysadmins_email`: The email that'll be used to build the cupsd.conf template - Default=`sysadmins@ansible_fqdn`
* `cups__debops_ferm_dependent_rules`: Default simple rules to open up ports (515, 631, 9100) through firewall that can be referenced when using [debops.ferm](https://github.com/debops/ansible-ferm) role.
* /etc/xinetd.d/cups-lpd
    * `cups_lpd_usn`: The username with which it'll run the cups-lpd process (through xinetd) - Default=`cupslpd`
* Optional templates:
    * They could've been setup as a simple file copy but accessing and adding ansible variables into it will not be possible. With this ansible\_managed, ansible\_fqdn, etc are accessible. The templates could also be simple text files with no variable declaration and it'll get copied over.
    * `cups_cupsd_conf_template`: For /etc/cups/cupsd.conf
    * `cups_cups_browsed_conf_template`: For /etc/cups/cups-browsed.conf
    * `cups_snmp_conf_template`: For /etc/cups/snmp.conf

### Installation and copying of PPDs:
* `cups_ppd_files_to_be_copied`: The folder to copy all .ppd files from - Default=None
* `cups_hplip`: Should it install HPLIP - Default=`True`
* `cups_ricoh_openprinting`: Should it install OpenPrinting-Ricoh drivers/PPDs - Default=`True`
* `cups_openprinting_apt_required`: This is defined as a ternary. It controls if the OpenPrinting APT key and repo is added based on Ricoh drivers are being installed or not. It can be easily overriden to your value.
* `cups_openprinting_apt_key_id`: The APT key id to obtain from keyserver below. Default=24CBF5474CFD1E2F
* `cups_openprinting_key_server`: The keyserver to acquire the key from for the below repo - Default=keyserver.ubuntu.com
* `cups_openprinting_repo`: The OpenPrinting Repo to add - Default="deb http://www.openprinting.org/download/printdriver/debian/ lsb3.2 main"


### Installation of Printers and classes:
* `cups_printer_uri_prefix`: A URI prefix for any filters on top of the URI - Default=""
* `cups_printer_report_ipp_supplies`: When printer object has no `report_ipp_supply_levels` attribute this value is used - Default=`True`
* `cups_printer_report_snmp_supplies`: When printer object has no `report_snmp_supply_levels` attribute this value is used. - Default=`True`
* `cups_printer_is_shared`: When printer object has no `shared` attribute this value is used - Default=`True`
* `cups_class_is_shared`: When the class object has no `shared` attribute this value is used - Default=`True`
* `cups_printer_list`: A **list** of hashes that contain printer information needed to install them. Please check [cups_lpadmin](library/cups_lpadmin.py) module and how [cups_printer_list](tasks/printer_install.yml) variable is used.
* `cups_class_list`: A **list** of hashes that contain class information needed to install them. Please check [cups_lpadmin](library/cups_lpadmin.py) module and how [cups_class_list](tasks/printer_install.yml) variable is used.
* `cups_purge_all_printers_and_classes`: Should the cups_lpadmin module purge/delete all printers before continuing.
* `cups_printers_and_classes_to_be_removed`: Printers and classes you would like to specifically remove.

### Variables related to operation of the role and general CUPS setup:
* `cups_packages_to_install`: The CUPS packages to install. This can be overridden for a specific package version if needed - Default=`cups, cups-pdf`
* `cups_xinetd_location`: The location of xinet.d files - Default=`/etc/xinetd.d`
* `cups_tmp_location`: Temp location that this role uses for copying files and running scripts. Location is created if it doesn't exist - Default=`/tmp/cups-ansible`
* `cups_admin_grp`: The group that has admin access to CUPS. This is referenced when adding users (if defined) to CUPS admin roles - Default=`lpadmin`
* `cups_services`: The CUPS service(s) that is referenced when starting and stopping CUPS service(s) for configuration purposes - Default=`cups`
* `cups_etc_location`: etc location of CUPS config - Default=`/etc/cups`
* `cups_etc_files_perms_owner`: Owner of files placed by this role under `cups_etc_location` - Default=`root`
* `cups_etc_files_perms_grp`: Group membership of files placed by this role under `cups_etc_location` - Default=`lp`
* `cups_etc_files_mode`: File mode of files placed by this role under `cups_etc_location` - Default=`0644`
* `cups_expect_pkgs`: The expect related packages that are installed for unattended installations of different expect scripts within this role - Default=`expect, python-pexpect`
* `cups_ppd_shared_location`: The standard shared location where PPDs can be placed and CUPS will pick them up - Default=`/opt/share/ppd`
* `cups_ricoh_ppd_location`: The location where Ricoh PPDs from OpenPrinting are installed - Default=`/opt/OpenPrinting-Ricoh/ppds/Ricoh`
