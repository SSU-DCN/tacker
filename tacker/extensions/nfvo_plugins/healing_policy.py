# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import abc
import six

from tacker._i18n import _
from tacker.common import exceptions
from tacker.services import service_base


@six.add_metaclass(abc.ABCMeta)
class HPluginBase(service_base.NFVPluginBase):

    @abc.abstractmethod
    def create_healing(self, context, healing):
        pass

    # @abc.abstractmethod
    # def delete_healing(self, context, healing_id):
    #     pass

    @abc.abstractmethod
    def get_healing(self, context, healing_id, fields=None):
        pass

    @abc.abstractmethod
    def get_healings(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def create_alert(self, context, alert):
        pass


class HPNotFound(exceptions.NotFound):
    message = _('NSD %(nsd_id)s could not be found')


class HPNotFound(exceptions.NotFound):
    message = _('NS %(ns_id)s could not be found')


class HPInUse(exceptions.InUse):
    message = _('NS %(ns_id)s in use')
