# -*- coding: utf-8 -*-
#
#
#    Authors: Guewen Baconnier
#    Copyright 2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#


class ChangesetMixin(object):

    def assert_changeset(self, partner, expected_changes):
        """ Check if a changeset has been created according to expected values

        The partner should have no prior changeset than the one created in the
        test (so it has exactly 1 changeset).

        The expected changes are tuples with (field, origin_value,
        new_value, state)

        :param partner: record of partner having a changeset
        :param expected_changes: contains tuples with the changes
        :type expected_changes: list(tuple))
        """
        changeset = self.env['res.partner.changeset'].search(
            [('partner_id', '=', partner.id)],
        )
        self.assertEqual(len(changeset), 1,
                         "1 changeset expected, got %s" % (changeset,))
        changes = changeset.change_ids
        missing = []
        for expected_change in expected_changes:
            for change in changes:
                if (change.field_id,
                        change.get_origin_value(),
                        change.get_new_value(),
                        change.state) == expected_change:
                    changes -= change
                    break
            else:
                missing.append(expected_change)
        message = u''
        for field, origin_value, new_value, state in missing:
            message += ("- field: '%s', origin_value: '%s', "
                        "new_value: '%s', state: '%s'\n" %
                        (field.name, origin_value, new_value, state))
        for change in changes:
            message += ("+ field: '%s', origin_value: '%s', "
                        "new_value: '%s', state: '%s'\n" %
                        (change.field_id.name,
                         change.get_origin_value(),
                         change.get_new_value(),
                         change.state))
        if message:
            raise AssertionError('Changes do not match\n\n:%s' % message)

    def _create_changeset(self, partner, changes):
        """ Create a changeset and its associated changes

        :param partner: 'res.partner' record
        :param changes: list of changes [(field, new value, state)]
        :returns: 'res.partner.changeset' record
        """
        ChangesetChange = self.env['res.partner.changeset.change']
        get_field = ChangesetChange.get_field_for_type
        change_values = []
        for field, value, state in changes:
            change = {
                'field_id': field.id,
                # write in the field of the appropriate type for the
                # origin field (char, many2one, ...)
                get_field(field, 'new'): value,
                'state': state,
            }
            change_values.append((0, 0, change))
        values = {
            'partner_id': partner.id,
            'change_ids': change_values,
        }
        return self.env['res.partner.changeset'].create(values)
