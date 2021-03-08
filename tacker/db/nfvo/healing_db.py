import sqlalchemy as sa

from tacker.db import model_base
from tacker.db import db_base
from tacker.db import types
from tacker.extensions.nfvo_plugins import healing_policy
from oslo_utils import timeutils
class HealingAction(model_base.BASE):
    __tablename__ = 'healing_policy'

    id = sa.Column(sa.Integer, primary_key=True, nullable=False,
                   autoincrement=True)
    event_id = sa.Column(types.Uuid, nullable=True)
    action_id = sa.Column(types.Uuid, nullable=False)
    action_type = sa.Column(sa.String(64), nullable=False)
    timestamp = sa.Column(sa.DateTime, nullable=False)
    policy_name = sa.Column(sa.String(64), nullable=False)



class HAPluginDb(healing_policy.HPluginBase, db_base.CommonDbMixin):
    def __init__(self):
        super(HAPluginDb, self).__init__()

    def _make_ha_dict(self, healing_db, fields=None):
        res = {}
        key_list = ('id', 'event_id', 'action_id', 'action_type', 'timestamp', 'policy_name')
        res.update((key, healing_db[key]) for key in key_list)
        return self._fields(res, fields)
    def get_healing(self, context, healing_id, fields=None):
        healing_db = self._get_by_id(context, HealingAction, healing_id)
        return self._make_ha_dict(healing_db)
    def get_healings(self, context, filters=None, fields=None):
        return self._get_collection(context, HealingAction,
                                    self._make_ha_dict,
                                    filters=filters, fields=fields)

    def _get_healing_by_event(self, context, event_id, fields=None):
        filterobj = {
            "event_id": [event_id]
        }
        return self._get_collection(context, HealingAction,
                                    self._make_ha_dict,
                                    filters=filterobj, fields=fields)

    def create_healing(self, context, healing):
        healing = healing.get('healing')
        print('hihi')
        with context.session.begin(subtransactions=True):
            healing_db = HealingAction(
                event_id=healing.get("event_id"),
                action_id=healing.get("action_id"),
                action_type=healing.get("action_type"),
                policy_name=healing.get("policy_name"),
                timestamp=timeutils.utcnow(),
            )
            context.session.add(healing_db)
        healing_dict = self._make_ha_dict(healing_db)
        return healing_dict

    