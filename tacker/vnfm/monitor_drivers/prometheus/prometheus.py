# All Rights Reserved.
#
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import netaddr
import requests
import time
import grpc
from string import Template
import copy
from oslo_log import log as logging
from oslo_serialization import jsonutils
from tacker.vnfm.monitor_drivers import abstract_driver
from tacker.vnfm.monitor_drivers.prometheus import service_pb2 as proto
from tacker.vnfm.monitor_drivers.prometheus import service_pb2_grpc
LOG = logging.getLogger(__name__)


class VNFMonitorPrometheus(abstract_driver.VNFMonitorAbstractDriver):
    params = ['application', 'OS']

    def __init__(self):
        self.kwargs = None
        self.vnf = None
        self.monitor_target = None
        self.prometheus_server = None

    def get_type(self):
        """Return one of predefined type of the hosting vnf drivers."""
        plugin_type = 'prometheus'
        return plugin_type

    def get_name(self):
        """Return a symbolic name for the VNF Monitor plugin."""
        plugin_name = 'prometheus'
        return plugin_name

    def get_description(self):
        """Return description of VNF Monitor plugin."""
        plugin_descript = 'Tacker VNFMonitor Prometheus Driver'
        return plugin_descript

    def monitor_get_config(self, plugin, context, vnf):
        """Return dict of monitor configuration data.

        :param plugin:
        :param context:
        :param vnf:
        :returns: dict
        :returns: dict of monitor configuration data
        """
        return {}

    def monitor_url(self, plugin, context, vnf):
        """Return the url of vnf to monitor.

        :param plugin:
        :param context:
        :param vnf:
        :returns: string
        :returns: url of vnf to monitor
        """
        pass

    @staticmethod
    def check_error(response):
        try:
            if 'result' not in response:
                raise ValueError
        except ValueError:
            LOG.error('Cannot request error : %s', response['error']['data'])

    def _set_prometheus_server(self, vdu):
        self.prometheus_server = {
            "ip": vdu['prometheus_server_ip'],
            "port": str(vdu['prometheus_server_port'])
        }

    def _set_monitor_target(self):
        vdus = []
        for vdu in self.kwargs['vdus']:
            alerts = self._create_alerts(
                alert_templates=self.kwargs['vdus'][vdu]['parameters']['alerts'], vdu_name=vdu)
            temp_vdu = proto.Vdu(vdu_name=vdu,
                                 mgmt_ip=self.kwargs['vdus'][vdu]['mgmt_ip'],
                                 exporter_port=str(
                                     self.kwargs['vdus'][vdu]['target_exporter_port']),
                                 alerts=alerts
                                 )

            self._set_prometheus_server(self.kwargs['vdus'][vdu])
            vdus.append(temp_vdu)

        self.monitor_target = proto.MonitorRequest(
            vnf_id=self.vnf['id'],
            vdus=vdus
        )

    def _create_alerts(self, alert_templates, vdu_name):
        alerts = []
        for key in alert_templates.keys():
            expr = Template(alert_templates[key]['expr'])
            unique_vdu_name = self.vnf['id'] + '_' + vdu_name
            parse_vdu_name = expr.substitute(vdu_name=unique_vdu_name)
            temp_alert = proto.Alert(
                group=key, alert=alert_templates[key]['alert'],
                expr=parse_vdu_name, duration=alert_templates[key]['for'],
                labels=alert_templates[key]['labels'], annotations=alert_templates[key]['annotations']
            )
            alerts.append(temp_alert)
        return alerts

    def _add_monitor_target(self):
        channel = grpc.insecure_channel(
            self.prometheus_server['ip'] + ':' + self.prometheus_server['port'])
        stub = service_pb2_grpc.MonitorStub(channel)
        response = stub.NewTargetRequest(self.monitor_target)
        LOG.debug('Grpc call result: %s', response.status)

    def _del_monitor_target(self):
        for vdu in self.kwargs['vdus']:
            self._set_prometheus_server(self.kwargs['vdus'][vdu])

        channel = grpc.insecure_channel(
            self.prometheus_server['ip'] + ':' + self.prometheus_server['port'])
        stub = service_pb2_grpc.MonitorStub(channel)
        vnf_id = proto.VnfId(vnf_id=self.vnf['id'])
        response = stub.DelTargetRequest(vnf_id)
        LOG.debug('Grpc call result: %s', response.status)

    def del_vnf_from_appmonitor(self, vnf, kwargs):
        self.__init__()
        self.vnf = vnf
        self.kwargs = kwargs
        self._del_monitor_target()

    def add_to_appmonitor(self, vnf, kwargs):
        self.__init__()
        self.kwargs = kwargs
        self.vnf = vnf
        self._set_monitor_target()
        self._add_monitor_target()

    def monitor_call(self, vnf, kwargs):
        pass

    def monitor_app_driver(self, plugin, context, vnf, service_instance):
        return self.get_name()
