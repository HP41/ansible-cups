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
    * Uses the template in the role to build the final config file(s) and paste it in the final location
    * It builds the following files: cupsd.conf, cups-browsed.conf and snmp.conf in /etc/cups/

### Install PPDs
* Creates `/opt/share/ppd` where CUPS looks for PPDs that are manually copied over.
* Adds OpenPrinting Repo.
* Install Ricoh OpenPrinting Package - `openprinting-ppds-postscript-ricoh`
    * Also unzip the PPDs it installs as the package installs them as gzip files in `/opt/OpenPrinting-Ricoh/ppds/Ricoh`
* Installs HPLIP:
    * Also installs the HP proprietary plugin using an except script.
* Copies over PPDs from the folder if specified in  `cups_ppd_files_to_be_copied` to `/opt/share/ppd`

### Install Printers
* Any printers defined to be removed will be removed first.
* Install Printers listed in the `cups_printer_list` variable and then installs classes listed in the `cups_class_list` 
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
* /etc/cups/cups-browsed.conf [Official Documentation](https://www.cups.org/documentation.html):
    * `cups_browsed_browse_remote_protocols`: Sets the value for `BrowseRemoteProtocols`- Default=`none`
    * `cups_browsed_browse_local_protocols`: Sets the value for `BrowseLocalProtocols` - Default=`none`
    * `cups_browsed_browse_protocols`: Sets the value for `BrowseProtocols` - Default=`none`
    * `cups_browsed_create_ipp_print_queues`: Sets the value for `CreateIPPPrinterQueues` - Default=`No`
    * `cups_browsed_print_servers_to_poll`: A **list** of IPs/DNS Names that defines what CUPS servers to poll to add their printers - `BrowsePoll` - Default=`None`
    * `cups_browsed_ips_or_subnets_to_search_for_printers`: A **list** of IPs/DNS Names that defines what servers (any type) to browse and add its printers - `BrowseAllow` - Default=`None` 
* /etc/cups/cupsd.conf [Official Documentation](https://www.cups.org/doc/man-cupsd.conf.html):
    * `cups_cupsd_admin_subnet`: The subnet which CUPS admin pages are limited to - Default=`all`
    * `cups_cupsd_preserve_job_history`: Preserve Job history in CUPS? - Default=`No`
    * `cups_cupsd_preserve_job_files`: Preserve Job Files in CUPS? - Default=`No`
    * `cups_cupsd_auto_purge_jobs`: Purge jobs right after they're completed? - Default=`Yes`
    * `cups_cupsd_require_user_to_be_part_of_to_access_admin_pages`: What local security group to be aprt of to be considered a CUPS admin and therefore gain access to the admin pages - Default=`@SYSTEM`
    * `cups_cupsd_limit_request_body`: Maximum size limit for print jobs coming in - Default=None
    * `cups_cupsd_conf_extra_policies`: Any extra CUPS policies to add to cupsd.conf. Please note this is treated as a string, therefore please ensure to maintain new line indentations using `|` when defining this variable.
* /etc/cups/snmp.conf [Official Documentation](https://www.cups.org/doc/man-cups-snmp.conf.html):
    * `cups_snmp_community_name`: The default community name with which it can search for printers - Default=`public`
    * `cups_snmp_locations_to_scan`: The IPs to scan.
* /etc/xinetd.d/cups-lpd    
    * `cups_lpd_usn`: The username with which it'll run the cups-lpd process (through xinetd) - Default=`snmp.conf`

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
* `cups_printer_list`: A **list** of hashes that contain printer information needed to install them. Please check [cups_lpadmin](library/cups_lpadmin.py) module on how to use it. 
* `cups_class_list`: A **list** of hashes that contain class information needed to install them. Please check [cups_lpadmin](library/cups_lpadmin.py) module on how to use it.
* `cups_purge_all_printers_and_classes`: Should the cups_lpadmin module purge/delete all printers before continuing.
* `cups_printers_and_classes_to_be_removed`: Printers and classes you would like to specifically remove.