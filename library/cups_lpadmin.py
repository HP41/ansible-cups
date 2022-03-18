#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
(c) 2015, David Symons (Multimac) <Mult1m4c@gmail.com>
(c) 2016, Konstantin Shalygin <k0ste@k0ste.ru>
(c) 2016, Hitesh Prabhakar <HP41@GitHub>

This file is part of Ansible

This module is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This software is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this software.  If not, see <http://www.gnu.org/licenses/>.
"""


# ===========================================


DOCUMENTATION = '''
---
module: cups_lpadmin
author:
    - "David Symons (Multimac) <Mult1m4c@gmail.com>"
    - "Konstantin Shalygin <k0ste@k0ste.ru>"
    - "Hitesh Prabhakar <H41P@GitHub>"
short_description: Manages printers in CUPS printing system.
description:
    - Creates, removes and sets options for printers in CUPS.
    - Creates, removes and sets options for classes in CUPS.
    - For class installation, the members are defined as a final state and therefore will only have the members defined.
version_added: "2.1"
notes: []
requirements:
    - CUPS 1.7+
options:
    name:
        description:
            - Name of the printer in CUPS.
        required: false
        default: null
    purge:
        description:
            - Task to purge all printers in CUPS. Convenient before deploy.
        required: false
        default: false
        choices: ["true", "false"]
    state:
        description:
            - Whether the printer should or not be in CUPS.
        required: false
        default: present
        choices: ["present", "absent"]
    printer_or_class:
        description:
            - State whether the object/item we are working on is a printer or class.
        required: false
        default: printer
        choices: ["printer", "class"]
    driver:
        description:
            - System V interface or PPD file.
        required: false
        default: model
        choices: ["model", "ppd"]
    uri:
        description:
            - The URI to use when connecting to the printer. This is only required in the present state.
        required: false
        default: null
    enabled:
        description:
            - Whether or not the printer should be enabled and accepting jobs.
        required: false
        default: true
        choices: ["true", "false"]
    shared:
        description:
            - Whether or not the printer should be shared on the network.
        required: false
        default: false
        choices: ["true", "false"]
    model:
        description:
            - The System V interface or PPD file to be used for the printer.
        required: false
        default: null
    default:
        description:
          - Set default server printer. Only one printer can be default.
        required: false
        default: false
        choices: ["true", "false"]
    info:
        description:
            - The textual description of the printer.
        required: false
        default: null
    location:
        description:
            - The textual location of the printer.
        required: false
        default: null
    assign_cups_policy:
        description:
            - Assign a policy defined in /etc/cups/cupsd.conf to this printer.
        required: false
        default: null
    class_members:
        description:
            - A list of printers to be added to this class.
        required: false
        default: []
        type: list
    report_ipp_supply_levels:
        description:
            - Whether or not the printer must report supply status via IPP.
        required: false
        default: true
        choices: ["true", "false"]
    report_snmp_supply_levels:
        description:
            - Whether or not the printer must report supply status via SNMP (RFC 3805).
        required: false
        default: true
        choices: ["true", "false"]
    job_kb_limit:
        description:
            - Limit jobs to this printer (in KB)
        required: false
        default: null
    job_quota_limit:
        description:
            - Sets the accounting period for per-user quotas. The value is an integer number of seconds.
        required: false
        default: null
    job_page_limit:
        description:
            - Sets the page limit for per-user quotas. The value is the integer number of pages that can be printed.
            - Double sided pages are counted as 2.
        required: false
        default: null
    options:
        description:
            - A dictionary of key-value pairs describing printer options and their required value.
        default: {}
        required: false
'''

# ===========================================


EXAMPLES = '''
# Creates HP MFP via ethernet, set default A4 paper size and make this printer
  as server default.
- cups_lpadmin:
    name: 'HP_M1536'
    state: 'present'
    printer_or_class: 'printer'
    uri: 'hp:/net/HP_LaserJet_M1536dnf_MFP?ip=192.168.1.2'
    model: 'drv:///hp/hpcups.drv/hp-laserjet_m1539dnf_mfp-pcl3.ppd'
    default: 'true'
    location: 'Room 404'
    info: 'MFP, but duplex broken, as usual on this model'
    printer_assign_policy: 'students'
    report_ipp_supply_levels: 'true'
    report_snmp_supply_levels: 'false'
    options:
      media: 'iso_a4_210x297mm'

# Creates HP Printer via IPP (shared USB printer in another CUPS instance).
  Very important include 'snmp=false' to prevent adopt 'parent' driver,
  because if 'parent' receive not raw job this job have fail (filter failed).
- cups_lpadmin:
    name: 'HP_P2055'
    state: 'present'
    uri: 'ipp://192.168.2.127:631/printers/HP_P2055?snmp=false'
    model: 'raw'
    options:
      media: 'iso_a4_210x297mm'

# Create CUPS Class.
- cups_lpadmin:
    name: 'StudentClass'
    state: 'present'
    printer_or_class: 'class'
    class_members:
        - CampusPrinter1
        - CampusPrinter2
    info: 'Printers for students'
    location: 'Room 404'

# Deletes the printers/classes.
- cups_lpadmin:
    name: 'HP_P2055'
    state: 'absent'
    printer_or_class: 'printer'
- cups_lpadmin:
    name: 'StudentClass'
    state: 'absent'
    printer_or_class: 'class'

# Purge all printers/classes. Useful when does not matter what we have now,
  client always receive new configuration.
- cups_lpadmin: purge='true'
'''

# ===========================================


RETURN = '''
purge:
    description: Whether to purge all printers on CUPS or not.
    returned: when purge=True
    type: string
    sample: "True"
state:
    description: The state as defined in the invocation of this script.
    returned: when purge=False
    type: string
    sample: "present"
printer_or_class:
    description: Printer or Class as defined when this script was invoked.
    returned: when purge=False
    type: string
    sample: "class"
name:
    description: The name of the destination (printer/class) as defined when the script was invoked.
    returned: when purge=False
    type: string
    sample: "Test-Printer"
uri:
    description: The uri of the printer.
    returned: when purge=False and printer_or_class=printer
    type: string
    sample: "ipp://192.168.2.127:631/printers/HP_P2055?snmp=false"
class_members:
    description: The members of the class.
    returned: when purge=False and printer_or_class=class
    type: string
    sample: "[TestPrinter1,TestPrinter2]"
assign_cups_policy:
    description: The CUPS policy to assign this printer or class.
    returned: when purge=False and (printer_or_class=class or printer_or_class=printer)
    type: string
    sample: "[TestPrinter1,TestPrinter2]"
changed:
    description: If any changes were made to the system when this script was run.
    returned: always
    type: boolean
    sample: "False"
stdout:
    description: Output from all the commands run concatenated. Only returned if any changes to the system were run.
    returned: always
    type: string
    sample: "sample output"
cmd_history:
    description: A concatenated string of all the commands run.
    returned: always
    type: string
    sample: "\nlpstat -p TEST \nlpinfo -l -m \nlpoptions -p TEST \nlpstat -p TEST \nlpstat -p TEST \nlpadmin -p TEST -o cupsIPPSupplies=true -o cupsSNMPSupplies=true \nlpoptions -p TEST -l "
'''


# ===========================================


class CUPSCommand(object):
    """
        This is the main class that directly deals with the lpadmin command.

        Method naming methodology:
            - Methods prefixed with 'cups_item' or '_cups_item' can be used with both printer and classes.
            - Methods prefixed with 'class' or '_class' are meant to work with classes only.
            - Methods prefixed with 'printer' or '_printer' are meant to work with printers only.

        CUPSCommand handles printers like so:
            - If state=absent:
                - Printer exists: Deletes printer
                - Printer doesn't exist: Does nothing and exits
            - If state=present:
                - Printer exists: Checks printer options and compares them to the ones stated:
                    - Options are different: Deletes the printer and installs it again with stated options.
                    - Options are same: Does nothing and exits.
                - Printer doesn't exist: Installs printer with stated options.
            - Mandatory options are set every time if the right variables are defined. They are:
                - cupsIPPSupplies
                - cupsSNMPSupplies
                - printer-op-policy
                - job-k-limit
                - job-page-limit
                - job-quota-period

        CUPSCommand handles classes like so:
            - If state=absent:
                - Class exists: Deletes class
                - Class doesn't exist: Does nothing and exits
            - If state=present:
                - Class exists: Checks class options and members and compares them to the ones stated:
                    - Options and members are different: Deletes the class and installs it again with
                      stated options and stated members.
                    - Options and members are same: Does nothing and exits.
                - Class doesn't exist: Installs class with stated options and members.
            - Mandatory options are set every time if the right variables are defined. They are:
                - cupsIPPSupplies
                - cupsSNMPSupplies
                - printer-op-policy
            - Notes about how classes are handled:
                - Members stated will be the final list of printers in that class.
                - It cannot add or remove printers from an existing list that might have more/other members defined.
                - It'll uninstall the class and create it from scratch as defined in this script if the defined member
                  list and the actual member list don't match.
    """

    def __init__(self, module):
        """
        Assigns module vars to object.
        """
        self.module = module

        self.driver = CUPSCommand.strip_whitespace(module.params['driver'])
        self.name = CUPSCommand.strip_whitespace(module.params['name'])
        self.printer_or_class = module.params['printer_or_class']

        self.state = module.params['state']
        self.purge = module.params['purge']

        self.uri = CUPSCommand.strip_whitespace(module.params['uri'])

        self.enabled = module.params['enabled']
        self.shared = module.params['shared']
        self.default = module.params['default']

        self.model = CUPSCommand.strip_whitespace(module.params['model'])

        self.info = CUPSCommand.strip_whitespace(module.params['info'])
        self.location = CUPSCommand.strip_whitespace(module.params['location'])

        self.options = module.params['options']

        self.assign_cups_policy = CUPSCommand.strip_whitespace(module.params['assign_cups_policy'])

        self.class_members = module.params['class_members']

        self.report_ipp_supply_levels = module.params['report_ipp_supply_levels']
        self.report_snmp_supply_levels = module.params['report_snmp_supply_levels']
        self.job_kb_limit = module.params['job_kb_limit']
        self.job_quota_limit = module.params['job_quota_limit']
        self.job_page_limit = module.params['job_page_limit']

        self.out = ""
        self.cmd_history = ""
        self.changed = False

        self.cups_current_options = {}
        self.cups_expected_options = {}
        self.class_current_members = []
        self.printer_current_options = {}

        self.check_mode = module.check_mode

        self.check_settings()

    def check_settings(self):
        """
        Checks the values provided to the module and see if there are any missing/illegal settings.

        Module fails and exits if it encounters an illegal combination of variables sent to the module.
        :returns: None
        """
        msgs = []

        if self.state == 'printer':
            if not self.printer_or_class:
                msgs.append("When state=present printer or class must be defined.")

            if self.printer_or_class == 'printer':
                if not self.uri and not self.exists_self():
                    msgs.append("URI is required to install printer.")

            if self.printer_or_class == 'class':
                if not self.class_members and not self.exists_self():
                    self.module.fail_json(msg="Empty class cannot be created.")

        if msgs:
            "\n".join(msgs)
            self.module.fail_json(msg=msgs)

    @staticmethod
    def strip_whitespace(text):
        """
        A static method to help with stripping white space around object variables.

        :returns: Trailing whitespace removed text or 'None' if input is 'None'.
        """
        try:
            return text.strip()
        except:
            return None

    def append_cmd_out(self, cmd_out):
        """
        Appends the out text from the command that was just run to the string with the out text of all the commands run.

        :param cmd_out: The text that was outputted during last command that was run.
        :returns: None
        """
        if cmd_out:
            self.out = "{0}{1}{2}".format(self.out, "\n", cmd_out)

    def append_cmd_history(self, cmd):
        """
        Appends the commands run into a single string.

        :param cmd: The command to be appended into the command history string.
        :returns: None
        """
        safe_cmd = ""
        for x in cmd:
            x = str(x)
            if " " in x:
                if not ((x.startswith('"') and x.endswith('"')) or (x.startswith("'") and x.endswith("'"))):
                    x = '{0}{1}{0}'.format('"', x)
            safe_cmd = "{0}{1}{2}".format(safe_cmd, x, " ")
        self.cmd_history = "{0}{1}{2}".format(self.cmd_history, "\n", safe_cmd)

    def _log_results(self, out):
        """
        Method to log the details outputted from the command that was just run.

        :param out: Output text from the command that was just run.
        :returns: None
        """
        self.append_cmd_out(out)

    def process_info_command(self, cmd):
        """
        Runs a command that's meant to poll information only.

        Wraps around _process_command and ensures command output isn't logged as we're just fetching for information.

        :param cmd: The command to run.
        :returns: The output of _process_command which is return code, command output and error output.
        """
        return self._process_command(cmd, log=False)

    def process_change_command(self, cmd, err_msg, only_log_on_error=False):
        """
        Runs a command that's meant to change CUPS state/settings.

        Wraps around _process_command and ensures command output is logged as we're making changes to the system.
        An optional only_log_on_error is provided for the install_mandatory_options methods that are always run
        almost always and need not pollute the changed/output text with its information. This'll ensure the output
        and error text is only recorded when there's an error (err != None) and (rc != 0).

        It also is an easy way to centralize change command therefore making support_check_mode easier to implement.

        :param cmd: The command to run.
        :param err_msg: The error message with which to exit the module if an error occurred.
        :param only_log_on_error: The optional flag to record output if there's an error. Default=False
        :returns: The output of _process_command which is return code, command output and error output.
        """
        (rc, out, err) = self._process_command(cmd, log=False)

        if rc != 0 and err:
            self.module.fail_json(msg="Error Message - {0}. Command Error Output - {1}.".format(err_msg, err))

        if self.check_mode:
            self.module.exit_json(changed=True)

        if not only_log_on_error:
            self._log_results(out)
            self.changed = True

        return rc, out, err

    def _process_command(self, cmd, log=True):
        """
        Runs a command given to it. Also logs the details if specified.

        :param cmd: The command to run.
        :param log: Boolean to specify if the command output should be logged. Default=True
        :returns: Return code, command output and error output of the command that was run.
        """
        self.append_cmd_history(cmd)

        (rc, out, err) = self.module.run_command(cmd)

        if log:
            self._log_results(out)

        return rc, out, err

    def _printer_get_installed_drivers(self):
        """
        Parses the output of lpinfo -l -m to provide a list of available drivers on machine.

        Example output from lpinfo -l -m:
        Model:  name = gutenprint.5.2://xerox-wc_m118/expert
                natural_language = en
                make-and-model = Xerox WorkCentre M118 - CUPS+Gutenprint v5.2.11
                device-id = MFG:XEROX;MDL:WorkCentre M118;DES:XEROX WorkCentre M118;

        The output is parsed into a hash and then placed into the value of another hash where the key is the name field:
        'gutenprint.5.2://xerox-wc_m118/expert': 'name': 'gutenprint.5.2://xerox-wc_m118/expert'
                                                 'natural_language': 'en'
                                                 'make-and-model': 'Xerox WorkCentre M118 - CUPS+Gutenprint v5.2.11'
                                                 'device-id': 'MFG:XEROX;MDL:WorkCentre M118;DES:XEROX WorkCentre M118;'

        :returns: Hash defining all the drivers installed on the system.
        """
        cmd = ['lpinfo', '-l', '-m']
        (rc, out, err) = self.process_info_command(cmd)

        # We want to split on sections starting with "Model:" as that specifies a new available driver
        prog = re.compile("^Model:", re.MULTILINE)
        cups_drivers = re.split(prog, out)

        drivers = {}
        for d in cups_drivers:

            # Skip if the line contains only whitespace
            if not d.strip():
                continue

            curr = {}
            for l in d.splitlines():
                kv = l.split('=', 1)

                # Strip out any excess whitespace from the key/value
                kv = tuple(map(str.strip, kv))

                curr[kv[0]] = kv[1]

            # Store drivers by their 'name' (i.e. path to driver file)
            drivers[curr['name']] = curr

        return drivers

    def _printer_get_all_printers(self):
        """
        Method to return all current printers and classes in CUPS.

        :returns: list of printer or classes names.
        """
        cmd = ['lpstat', '-a']
        (rc, out, err) = self.process_info_command(cmd)
        all_printers = []

        if rc == 0:
            # Match only 1st column, where placed printer name
            all_printers = [line.split()[0] for line in out.splitlines()]

        return all_printers

    def cups_purge_all_items(self):
        """
        Purge all printers and classes installed on CUPS.
        """
        all_printers = self._printer_get_all_printers()

        for printer in all_printers:
            self.cups_item_uninstall(item_to_uninstall=printer)

    def _printer_get_make_and_model(self):
        """
        Method to return the make and model of the driver/printer that is supplied to the object.

        If ppd is provided, ignore this as the ppd provided takes priority over finding a driver.

        If not ppd is provided (default behaviour), the model specified is used.
        It checks to see if the model specified is in the list of drivers installed on the system. If not, the whole
        module fails out with an error message.

        :returns: make-and-model of the model specified.
        """
        if self.driver == 'model':
            # Raw printer is defined
            if not self.model or self.model == 'raw':
                return "Remote Printer"
        elif self.driver == 'ppd':
            return

        installed_drivers = self._printer_get_installed_drivers()

        if self.model in installed_drivers:
            return installed_drivers[self.model]['make-and-model']

        self.module.fail_json(msg="Unable to determine printer make and model for printer '{0}'.".format(self.model))

    def _printer_install(self):
        """
        Installs the printer with the settings defined.
        """
        cmd = ['lpadmin', '-p', self.name, '-v', self.uri]

        if self.enabled:
            cmd.append('-E')

        if self.shared:
            cmd.extend(['-o', 'printer-is-shared=true'])
        else:
            cmd.extend(['-o', 'printer-is-shared=false'])

        if self.model:
            if self.driver == 'model':
                cmd.extend(['-m', self.model])
            elif self.driver == 'ppd':
                cmd.extend(['-P', self.model])

        if self.info:
            cmd.extend(['-D', self.info])

        if self.location:
            cmd.extend(['-L', self.location])

        self.process_change_command(cmd,
                                    err_msg="Installing printer '{0}' failed"
                                    .format(self.name))

        if self.default:
            cmd = ['lpadmin', '-d', self.name]
            self.process_change_command(cmd,
                                        err_msg="Setting printer '{0}' as default failed"
                                        .format(self.name))

    def _printer_install_mandatory_options(self):
        """
        Installs mandatory printer options.

        cupsIPPSupplies, cupsSNMPSupplies, job-k-limit, job-page-limit, printer-op-policy,job-quota-period
        cannot be checked via cups command-line tools yet. Therefore force set these options if they are defined.
        If there's an error running the command, the whole module will fail with an error message.
        """
        orig_cmd = ['lpadmin', '-p', self.name]
        cmd = list(orig_cmd)  # Making a copy of the list/array

        if self.report_ipp_supply_levels:
            cmd.extend(['-o', 'cupsIPPSupplies=true'])
        else:
            cmd.extend(['-o', 'cupsIPPSupplies=false'])

        if self.report_snmp_supply_levels:
            cmd.extend(['-o', 'cupsSNMPSupplies=true'])
        else:
            cmd.extend(['-o', 'cupsSNMPSupplies=false'])

        if self.job_kb_limit:
            cmd.extend(['-o', 'job-k-limit={0}'.format(self.job_kb_limit)])

        if self.job_page_limit:
            cmd.extend(['-o', 'job-page-limit={0}'.format(self.job_page_limit)])

        if self.job_quota_limit:
            cmd.extend(['-o', 'job-quota-period={0}'.format(self.job_quota_limit)])

        if self.assign_cups_policy:
            cmd.extend(['-o', 'printer-op-policy={0}'.format(self.assign_cups_policy)])

        if cmd != orig_cmd:
            self.process_change_command(cmd,
                                        err_msg="Install mandatory options for printer '{0}'"
                                        .format(self.name),
                                        only_log_on_error=True)

    def _printer_install_options(self):
        """
        Installs any printer driver specific options defined.

        :returns: rc, out, err. The output of the lpadmin installation command.
        """
        cmd = ['lpadmin', '-p', self.name]

        for k, v in self.options.items():
            cmd.extend(['-o', '{0}={1}'.format(k, v)])

        if self.default:
            cmd.extend(['-d', self.name])

        return self.process_change_command(cmd,
                                           err_msg="Install printer options for printer '{0}' failed".format(self.name))

    def _class_install(self):
        """
        Installs the class with the settings defined.

        It loops through the list of printers that are supposed to be in the class and confirms if they exists and
        adds them to the class. If any one of the printers don't exist, the whole module will fail with an error
        message.
        """
        for printer in self.class_members:
            # Going through all the printers that are supposed to be in the class and adding them to said class
            # Ensuring first the printer exists
            if self.exists(item_to_check=printer):
                cmd = ['lpadmin', '-p', printer, '-c', self.name]
                self.process_change_command(cmd,
                                            err_msg="Failed to add printer '{0}' to class '{1}'"
                                            .format(printer, self.name))
            else:
                self.module.fail_json(msg="Printer '{0}' doesn't exist and cannot be added to class '{1}'."
                                      .format(printer, self.name))

        # Now that the printers are added to the class and the class created, we are setting up a few
        # settings for the class itself
        if self.exists_self():
            cmd = ['lpadmin', '-p', self.name]

            if self.enabled:
                cmd.append('-E')

            if self.shared:
                cmd.extend(['-o', 'printer-is-shared=true'])
            else:
                cmd.extend(['-o', 'printer-is-shared=false'])

            if self.info:
                cmd.extend(['-D', self.info])

            if self.location:
                cmd.extend(['-L', self.location])

            self.process_change_command(cmd,
                                        err_msg="Failed to set Class options for class '{0}'"
                                        .format(self.name))

    def _class_install_mandatory_options(self):
        """
        Installs mandatory class options.

        cupsIPPSupplies, cupsSNMPSupplies, printer-op-policy,job-quota-period cannot be checked via
        cups command-line tools yet. Therefore force set these options if they are defined.
        If there's an error running the command, the whole module will fail with an error message.
        """
        orig_cmd = ['lpadmin', '-p', self.name]
        cmd = list(orig_cmd)  # Making a copy of the list/array

        if self.report_ipp_supply_levels:
            cmd.extend(['-o', 'cupsIPPSupplies=true'])
        else:
            cmd.extend(['-o', 'cupsIPPSupplies=false'])

        if self.report_snmp_supply_levels:
            cmd.extend(['-o', 'cupsSNMPSupplies=true'])
        else:
            cmd.extend(['-o', 'cupsSNMPSupplies=false'])

        if self.assign_cups_policy:
            cmd.extend(['-o', 'printer-op-policy={0}'.format(self.assign_cups_policy)])

        if cmd != orig_cmd:
            self.process_change_command(cmd,
                                        err_msg="Installing mandatory options for class '{0}' failed"
                                        .format(self.name),
                                        only_log_on_error=True)

    def cups_item_uninstall_self(self):
        """
        Uninstalls the printer or class defined in this class.
        """
        self.cups_item_uninstall(item_to_uninstall=self.name)

    def cups_item_uninstall(self, item_to_uninstall):
        """
        Uninstalls a printer or class given in item_to_uninstall if it exists else do nothing.

        :param item_to_uninstall: the CUPS Item (Printer or Class) that needs to be uninstalled.
        """
        cmd = ['lpadmin', '-x']

        if self.exists(item_to_check=item_to_uninstall):
            if item_to_uninstall:
                cmd.append(item_to_uninstall)
                self.process_change_command(cmd,
                                            err_msg="Uninstalling CUPS Item '{0}' failed"
                                            .format(item_to_uninstall))
            else:
                self.module.fail_json(msg="Cannot delete/uninstall a cups item (printer/class) with no name.")

    def exists_self(self):
        """
        Checks to see if the printer or class defined in this class exists.

        Using the lpstat command and based on if an error code is returned it can confirm if a printer or class exists.

        :returns: The return value of self.exists()
        """
        return self.exists(item_to_check=self.name)

    def exists(self, item_to_check=None):
        """
        Checks to see if a printer or class exists.

        Using the lpstat command and based on if an error code is returned it can confirm if a printer or class exists.

        :param item_to_check: The print or class name to check if it exists.

        :returns: True if return code form the command is 0 and therefore there where no errors and printer/class
        exists. Module exits if item_to_check is not defined.
        """
        if item_to_check:
            cmd = ['lpstat', '-p', item_to_check]
            (rc, out, err) = self.process_info_command(cmd)
            return rc == 0
        else:
            self.module.fail_json(msg="Cannot check if a cups item (printer/class) exists that has no name.")

    def cups_item_get_cups_options(self):
        """
        Returns a list of currently set options for the printer or class.

        Uses lpoptions -p command to list all the options, eg:
            copies=1 device-uri=socket://127.0.0.1:9100 finishings=3 job-cancel-after=10800
            job-hold-until=no-hold job-priority=50 job-sheets=none,none marker-change-time=0 number-up=1
            printer-commands=AutoConfigure,Clean,PrintSelfTestPage printer-info='HP LaserJet 4250 Printer Info'
            printer-is-accepting-jobs=true printer-is-shared=true printer-location=PrinterLocation
            printer-make-and-model='HP LaserJet 4250 Postscript (recommended)' printer-state=3
            printer-state-change-time=1463902120 printer-state-reasons=none printer-type=8425668
            printer-uri-supported=ipp://localhost/printers/TestPrinter

        :returns: A hash of the above info.
        """
        cmd = ['lpoptions', '-p', self.name]
        (rc, out, err) = self.process_info_command(cmd)

        options = {}
        for s in shlex.split(out):
            kv = s.split('=', 1)

            if len(kv) == 1:  # If we only have an option name, set it's value to None
                options[kv[0]] = None
            elif len(kv) == 2:  # Otherwise set it's value to what we received
                options[kv[0]] = kv[1]

        self.cups_current_options = options

        return options

    def printer_check_cups_options(self):
        """
        Creates a hash of the defined options sent to this module.
        Polls and retrieves a hash of options currently set for the printer.
        Compares them and returns True if the option values are satisfied or False if not satisfied.

        :returns: 'True' if the option values match else 'False'.
        """
        expected_cups_options = {
            'printer-make-and-model': self._printer_get_make_and_model(),
            'printer-is-shared': 'true' if self.shared else 'false',
        }

        if self.info:
            expected_cups_options['printer-info'] = self.info
        if self.uri:
            expected_cups_options['device-uri'] = self.uri
        if self.location:
            expected_cups_options['printer-location'] = self.location

        self.cups_expected_options = expected_cups_options

        cups_options = self.cups_item_get_cups_options()

        # Comparing expected options as stated above to the options of the actual printer object.
        for k in expected_cups_options:
            if k not in cups_options:
                return False

            if expected_cups_options[k] != cups_options[k]:
                return False

        return True

    def class_check_cups_options(self):
        """
        Creates a hash of the defined options sent to this module.
        Polls and retrieves a hash of options currently set for the class.
        Compares them and returns True if the option values are satisfied or False if not satisfied.

        :returns: 'True' if the option values match else 'False'.
        """
        expected_cups_options = {
            'printer-location': self.location,
        }

        if self.info:
            expected_cups_options['printer-info'] = self.info
        if self.location:
            expected_cups_options['printer-location'] = self.location

        self.cups_expected_options = expected_cups_options

        options = self.cups_item_get_cups_options()
        options_status = True

        # Comparing expected options as stated above to the options of the actual class object
        for k in expected_cups_options:
            if k not in options:
                options_status = False
                break

            if expected_cups_options[k] != options[k]:
                options_status = False
                break

        # Comparing expected class members and actual class members
        class_members_status = sorted(self.class_members) == sorted(self.class_get_current_members())

        return options_status and class_members_status

    def class_get_current_members(self):
        """
        Uses the lpstat -c command to get a list of members, eg:
        members of class TestClass:
            TestPrinter1
            TestPrinter2

        This is parsed into a list. The first line is skipped.

        :returns: A list of members for class specified in the module.
        """
        cmd = ['lpstat', '-c', self.name]
        (rc, out, err) = self.process_info_command(cmd)

        if rc != 0:
            self.module.fail_json(
                msg="Error occurred while trying to discern class '{0}' members.".format(self.name))

        members = []
        # Skip first line as it's an information line, it end with a ':'
        (info, out) = out.split(':', 1)
        out = shlex.split(out)
        for m in out:
            str.strip(m)
            members.append(m)

        self.class_current_members = members

        return members

    def printer_get_specific_options(self):
        """
        Returns a hash of printer specific options with its current value, available values and its label.
        Runs lpoptions -p <printer_name> -l, eg:
            HPCollateSupported/Collation in Printer: True288 *False288
            HPOption_500_Sheet_Feeder_Tray3/Tray 3: *True False
            HPOption_Duplexer/Duplex Unit: *True False
            HPOption_Disk/Printer Disk: True *False
            HPOption_PaperPolicy/Paper Matching: *Prompt Scale Crop
            HPServicesWeb/Services on the Web: *SupportAndTroubleshooting ProductManuals ColorPrintingAccessUsage
                OrderSupplies ShowMeHow
            HPServicesUtility/Device Maintenance: *DeviceAndSuppliesStatus
            Resolution/Printer Resolution: *600dpi 1200dpi
            PageSize/Page Size: *Letter Legal Executive HalfLetter w612h936 4x6 5x7 5x8 A4 A5 A6 RA4 B5 B6 W283H425
                w553h765 w522h737 w558h774 DoublePostcard Postcard Env10 Env9 EnvMonarch EnvISOB5 EnvC5 EnvC6 EnvDL
                Custom.WIDTHxHEIGHT
            InputSlot/Paper Source: *Auto Tray1 Tray2 Tray3 Tray1_Man
            Duplex/2-Sided Printing: *None DuplexNoTumble DuplexTumble
            Collate/Collate: True *False

        This is parsed into a hash with option name as key and value with currently selected option,
        label of the option and available values eg:
            'HPCollateSupported': 'current': 'False288'
                                  'label': 'Collation in Printer'
                                  'values': 'True288'
                                            'False288'

        :returns: A hash of printer options. It includes currently set option and other available options.
        """
        cmd = ['lpoptions', '-p', self.name, '-l']
        (rc, out, err) = self.process_info_command(cmd)

        options = {}
        for l in out.splitlines():
            remaining = l

            (name, remaining) = remaining.split('/', 1)
            (label, remaining) = remaining.split(':', 1)

            values = shlex.split(remaining)

            current_value = None
            for v in values:
                # Current value is prepended with a '*'
                if not v.startswith('*'):
                    continue

                v = v[1:]  # Strip the '*' from the value

                current_value = v
                break

            options[name] = {
                'current': current_value,
                'label': label,
                'values': values,
            }

        self.printer_current_options = options

        return options

    def printer_check_options(self):
        """
        Returns if the defined options is the same as the options currently set for the printer.
        :returns: Returns if the defined options is the same as the options currently set for the printer.
        """
        expected_printer_options = self.options

        printer_options = self.printer_get_specific_options()
        for k in expected_printer_options:
            if k not in printer_options:
                return False

            if expected_printer_options[k] != printer_options[k]['current']:
                return False

        return True

    def printer_install(self):
        """
        The main method that's called when state is 'present' and printer_or_class is 'printer'.

        It checks to see if printer exists and if its settings are the same as defined.
        If not, it deletes it.

        It then checks to see if it exists again and installs it with defined settings if it doesn't exist.

        It also installs mandatory settings.

        Lastly it sets the printer specific options to the printer if it isn't the same.
        """
        if self.exists_self() and not self.printer_check_cups_options():
            self.cups_item_uninstall_self()

        if not self.exists_self():
            self._printer_install()

        # cupsIPPSupplies, cupsSNMPSupplies, job-k-limit, job-page-limit, printer-op-policy,
        # job-quota-period cannot be checked via cups command-line tools yet
        # Therefore force set these options if they exist
        if self.exists_self():
            self._printer_install_mandatory_options()

        if not self.printer_check_options():
            self._printer_install_options()

    def class_install(self):
        """
        The main method that's called when state is 'present' and printer_or_class is 'class'.

        It checks to see if class exists and if its settings are the same as defined.
        If not, it deletes it.

        It then checks to see if it exists again and installs it with defined settings if it doesn't exist.

        It also installs mandatory settings.
        """
        if self.exists_self() and not self.class_check_cups_options():
            self.cups_item_uninstall_self()

        if not self.exists_self():
            self._class_install()

        if self.exists_self():
            self._class_install_mandatory_options()

    def start_process(self):
        """
        This starts the process of processing the information provided to the module.

        Based on state, the following is done:
        - state=present:
            - printer_or_class=printer:
                - Call CUPSCommand.printer_install() to install the printer.
            - printer_or_class=class:
                - Call CUPSCommand.class_install() to install the class.
        - state=absent:
            - Call CUPSCommand.cups_item_uninstall() to uninstall either a printer or a class.

        :returns: 'result' a hash containing the desired state.
        """
        result = {}

        if self.purge:
            self.cups_purge_all_items()
            result['purge'] = self.purge

        else:
            result['state'] = self.state
            result['printer_or_class'] = self.printer_or_class
            result['assign_cups_policy'] = self.assign_cups_policy
            result['name'] = self.name

            if self.printer_or_class == 'printer':
                if self.state == 'present':
                    self.printer_install()
                else:
                    self.cups_item_uninstall_self()
                result['uri'] = self.uri

            else:
                if self.state == 'present':
                    self.class_install()
                else:
                    self.cups_item_uninstall_self()
                result['class_members'] = self.class_members

        result['changed'] = self.changed

        if self.out:
            result['stdout'] = self.out

        # Verbose Logging info
        if self.cmd_history:
            result['cmd_history'] = self.cmd_history
        if self.cups_current_options:
            result['cups_current_options'] = self.cups_current_options
        if self.cups_expected_options:
            result['cups_expected_options'] = self.cups_expected_options
        if self.class_current_members:
            result['class_current_members'] = self.class_current_members
        if self.printer_current_options:
            result['printer_current_options'] = self.printer_current_options

        return result


# ===========================================


def main():
    """
    main function that populates this Ansible module with variables and sets it in motion.

    First an Ansible Module is defined with the variable definitions and default values.
    Then a CUPSCommand is created using using this module. CUPSCommand populates its own values with the module vars.

    This CUPSCommand's start_process() method is called to begin processing the information provided to the module.

    Records the rc, out, err values of the commands run above and accordingly exists the module and sends the status
    back to to Ansible using module.exit_json().
    """
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(required=False, default='present', choices=['present', 'absent'], type='str'),
            driver=dict(required=False, default='model', choices=['model', 'ppd'], type='str'),
            purge=dict(required=False, default=False, type='bool'),
            name=dict(required=False, type='str'),
            printer_or_class=dict(default='printer', required=False, type='str', choices=['printer', 'class']),
            uri=dict(required=False, default=None, type='str'),
            enabled=dict(required=False, default=True, type='bool'),
            shared=dict(required=False, default=False, type='bool'),
            default=dict(required=False, default=False, type='bool'),
            model=dict(required=False, default=None, type='str'),
            info=dict(required=False, default=None, type='str'),
            location=dict(required=False, default=None, type='str'),
            assign_cups_policy=dict(required=False, default=None, type='str'),
            class_members=dict(required=False, default=[], type='list'),
            report_ipp_supply_levels=dict(required=False, default=True, type='bool'),
            report_snmp_supply_levels=dict(required=False, default=True, type='bool'),
            job_kb_limit=dict(required=False, default=None, type='int'),
            job_quota_limit=dict(required=False, default=None, type='int'),
            job_page_limit=dict(required=False, default=None, type='int'),
            options=dict(required=False, default={}, type='dict'),
        ),
        supports_check_mode=True,
        required_one_of=[['name', 'purge']],
        mutually_exclusive=[['name', 'purge']]
    )

    cups_command = CUPSCommand(module)
    result_info = cups_command.start_process()
    module.exit_json(**result_info)

# Import statements at the bottom as per Ansible best practices.
from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
