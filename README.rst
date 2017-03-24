CI status reporting
===================

This is a simple tool to collect and analyze statistics of CI jobs runs.
It uses information from Gerrit on how CI jobs voted.

Installation
------------

The tool does not access Gerrit API directly, but uses an existing `gertty
<https://github.com/openstack/gertty>`_ database instead. So, make sure you
have it configured and populated with recent reviews. The tool also requires
`PyYAML <http://pyyaml.org/>`_.

Once all dependencies are installed, you can use the tool from the working
directory as described in Usage_.

Usage
-----

Collect statistics using the following command::

    ./collect-stats.py openstack/ironic

Replace ``openstack/ironic`` with your Gerrit project name.
This command collects all CI runs from last 30 days (configurable) and outputs
their result in file called ``ci-stats.yaml`` (configurable). The ``master``
branch is used by default (also configurable).

The next command takes this file and generates a report from it::

    ./gen-report.py

See ``./gen-report.py --help`` for usage details.
The resulting file is called ``ci-report.yaml`` by default.

Example
-------

The resulting file may look like this::

    jobs:
      gate-tempest-dsvm-ironic-inspector-ubuntu-xenial-nv:
        failure_rate: 0.23792486583184258
        failures: 133
        runs: 559
      gate-tempest-dsvm-ironic-ipa-partition-agent_ipmitool-tinyipa-python3-ubuntu-xenial-nv:
        failure_rate: 1.0
        failures: 7
        runs: 7
      gate-tempest-dsvm-ironic-ipa-partition-bios-agent_ipmitool-tinyipa-ubuntu-xenial:
        failure_rate: 0.15780141843971632
        failures: 89
        runs: 564
      gate-tempest-dsvm-ironic-ipa-partition-bios-ipmi-tinyipa-ubuntu-xenial-nv:
        failure_rate: 0.13140311804008908
        failures: 59
        runs: 449
      gate-tempest-dsvm-ironic-ipa-partition-bios-pxe_ipmitool-tinyipa-ubuntu-xenial:
        failure_rate: 0.1524822695035461
        failures: 86
        runs: 564
      gate-tempest-dsvm-ironic-ipa-partition-pxe_ipmitool-tinyipa-python3-ubuntu-xenial-nv:
        failure_rate: 1.0
        failures: 54
        runs: 54
      gate-tempest-dsvm-ironic-ipa-partition-uefi-pxe_ipmitool-tinyipa-ubuntu-xenial-nv:
        failure_rate: 0.15742397137745975
        failures: 88
        runs: 559
      gate-tempest-dsvm-ironic-ipa-resourceclasses-partition-pxe_ipmitool-tinyipa-ubuntu-xenial-nv:
        failure_rate: 0.08196721311475409
        failures: 5
        runs: 61
      gate-tempest-dsvm-ironic-ipa-wholedisk-agent_ipmitool-tinyipa-multinode-ubuntu-xenial:
        failure_rate: 0.14035087719298245
        failures: 56
        runs: 399
      gate-tempest-dsvm-ironic-ipa-wholedisk-agent_ipmitool-tinyipa-multinode-ubuntu-xenial-nv:
        failure_rate: 0.3058823529411765
        failures: 52
        runs: 170
      gate-tempest-dsvm-ironic-ipa-wholedisk-bios-agent_ipmitool-tinyipa-ubuntu-xenial:
        failure_rate: 0.1524822695035461
        failures: 86
        runs: 564
      gate-tempest-dsvm-ironic-ipa-wholedisk-bios-pxe_ipmitool-tinyipa-ubuntu-xenial:
        failure_rate: 0.15780141843971632
        failures: 89
        runs: 564
      gate-tempest-dsvm-ironic-ipa-wholedisk-bios-pxe_snmp-tinyipa-ubuntu-xenial-nv:
        failure_rate: 0.4007155635062612
        failures: 224
        runs: 559
      gate-tempest-dsvm-ironic-multitenant-network-ubuntu-xenial:
        failure_rate: 0.12716763005780346
        failures: 22
        runs: 173
      gate-tempest-dsvm-ironic-parallel-ubuntu-xenial-nv:
        failure_rate: 1.0
        failures: 61
        runs: 61
      gate-tempest-dsvm-ironic-pxe_ipa-full-ubuntu-xenial-nv:
        failure_rate: 1.0
        failures: 61
        runs: 61
      gate-tempest-dsvm-ironic-pxe_ipmitool-postgres-ubuntu-xenial-nv:
        failure_rate: 0.1413237924865832
        failures: 79
        runs: 559
    worst_failure_rates:
    - job: gate-tempest-dsvm-ironic-ipa-partition-pxe_ipmitool-tinyipa-python3-ubuntu-xenial-nv
      rate: 1.0
    - job: gate-tempest-dsvm-ironic-pxe_ipa-full-ubuntu-xenial-nv
      rate: 1.0
    - job: gate-tempest-dsvm-ironic-parallel-ubuntu-xenial-nv
      rate: 1.0
    - job: gate-tempest-dsvm-ironic-ipa-partition-agent_ipmitool-tinyipa-python3-ubuntu-xenial-nv
      rate: 1.0
