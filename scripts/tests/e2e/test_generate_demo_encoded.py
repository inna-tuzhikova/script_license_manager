import json
from datetime import date, timedelta

from django.conf import settings
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from .fixtures import (
    default_json_schema,
    get_default_script,
    get_default_user,
    give_permission_to_user,
    update_script,
)


class GenerateDemoEncodedPermissionsTests(APITestCase):
    def setUp(self):
        self.user = get_default_user()
        self.client.force_login(self.user)
        self.script = get_default_script()

    def test_not_authorized_user(self):
        self.client.logout()
        response = self.client.post(
            reverse(
                'scripts:script-generate-demo-encoded',
                kwargs=dict(pk=self.script.id)
            ),
            dict(license_key='0x12345678')
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_not_downloadable_script_wo_force_perms(self):
        not_downloadable = [
            dict(is_active=False, enabled=True),
            dict(is_active=True, enabled=False),
            dict(is_active=False, enabled=False),
        ]
        for params in not_downloadable:
            update_script(self.script, **params)
            response = self.client.post(reverse(
                'scripts:script-generate-demo-encoded',
                kwargs=dict(pk=self.script.id)
            ))
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_downloadable_script_w_force_perms(self):
        give_permission_to_user(self.user, 'force_issue_encoded_script')

        not_downloadable = [
            dict(is_active=False, enabled=True),
            dict(is_active=True, enabled=False),
            dict(is_active=False, enabled=False),
        ]
        for params in not_downloadable:
            update_script(self.script, **params)
            response = self.client.post(reverse(
                'scripts:script-generate-demo-encoded',
                kwargs=dict(pk=self.script.id)
            ))
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_script_not_allowing_encoded_lk_issue_wo_force_perms(self):
        update_script(self.script, allow_issue_encoded_lk=False)
        response = self.client.post(
            reverse(
                'scripts:script-generate-demo-encoded',
                kwargs=dict(pk=self.script.id)
            ),
            dict(license_key='0x12345678')
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_script_not_allowing_encoded_lk_issue_w_force_perms(self):
        give_permission_to_user(self.user, 'force_issue_encoded_script')

        update_script(self.script, allow_issue_encoded_lk=False)
        response = self.client.post(
            reverse(
                'scripts:script-generate-demo-encoded',
                kwargs=dict(pk=self.script.id)
            ),
            dict(license_key='0x12345678')
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_script_allowing_encoded_lk_issue_wo_force_perms(self):
        response = self.client.post(
            reverse(
                'scripts:script-generate-demo-encoded',
                kwargs=dict(pk=self.script.id)
            ),
            dict(license_key='0x12345678')
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_script_allowing_encoded_lk_issue_w_force_perms(self):
        give_permission_to_user(self.user, 'force_issue_encoded_script')

        response = self.client.post(
            reverse(
                'scripts:script-generate-demo-encoded',
                kwargs=dict(pk=self.script.id)
            ),
            dict(license_key='0x12345678')
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_script_not_allowing_encoded_lk_exp_issue_wo_force_perms(self):
        update_script(self.script, allow_issue_encoded_lk_exp=False)
        response = self.client.post(
            reverse(
                'scripts:script-generate-demo-encoded',
                kwargs=dict(pk=self.script.id)
            ),
            dict(
                expires=(date.today() + timedelta(days=10)).isoformat(),
                license_key='0x12345678'
            )
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_script_not_allowing_encoded_lk_exp_issue_w_force_perms(self):
        give_permission_to_user(self.user, 'force_issue_encoded_script')

        update_script(self.script, allow_issue_encoded_lk_exp=False)
        response = self.client.post(
            reverse(
                'scripts:script-generate-demo-encoded',
                kwargs=dict(pk=self.script.id)
            ),
            dict(
                expires=(date.today() + timedelta(days=10)).isoformat(),
                license_key='0x12345678'
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_script_allowing_encoded_lk_exp_issue_wo_force_perms(self):
        response = self.client.post(
            reverse(
                'scripts:script-generate-demo-encoded',
                kwargs=dict(pk=self.script.id)
            ),
            dict(
                expires=(date.today() + timedelta(days=10)).isoformat(),
                license_key='0x12345678'
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_script_allowing_encoded_lk_exp_issue_w_force_perms(self):
        give_permission_to_user(self.user, 'force_issue_encoded_script')

        response = self.client.post(
            reverse(
                'scripts:script-generate-demo-encoded',
                kwargs=dict(pk=self.script.id)
            ),
            dict(
                expires=(date.today() + timedelta(days=10)).isoformat(),
                license_key='0x12345678'
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GenerateDemoEncodedValidationTests(APITestCase):
    def setUp(self):
        self.user = get_default_user()
        self.client.force_login(self.user)
        self.script = get_default_script()

    def test_not_existing_script(self):
        response = self.client.post(reverse(
            'scripts:script-generate-demo-encoded',
            kwargs=dict(pk='not_existing_script')
        ))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_empty_request(self):
        response = self.client.post(
            reverse(
                'scripts:script-generate-demo-encoded',
                kwargs=dict(pk=self.script.pk)
            ),
            dict()
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_params(self):
        future_dt = (date.today() + timedelta(days=10)).isoformat()
        valid_params = [
            dict(license_key='0x12345678', expires=None, extra_params=None),
            dict(license_key='0x12345678', expires=None),
            dict(license_key='0x12345678'),
            dict(license_key='0x12345678', expires=future_dt),
        ]
        for params in valid_params:
            response = self.client.post(
                reverse(
                    'scripts:script-generate-demo-encoded',
                    kwargs=dict(pk=self.script.pk)
                ),
                params,
                format='json'
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_valid_extra_params(self):
        valid_extra_params = [
            None,
            json.dumps({}),
            json.dumps(dict(a=1, b=2))
        ]
        for params in valid_extra_params:
            response = self.client.post(
                reverse(
                    'scripts:script-generate-demo-encoded',
                    kwargs=dict(pk=self.script.pk)
                ),
                dict(extra_params=params, license_key='0x12345678'),
                format='json'
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        update_script(self.script, extra_params_schema=default_json_schema)
        valid_extra_params = [
            json.dumps(dict(a=1, b='b1')),
            json.dumps(dict(a=2, b='b2')),
            json.dumps(dict(a=7, b='b3')),
            json.dumps(dict(a=10, b='b2')),
        ]
        for params in valid_extra_params:
            response = self.client.post(
                reverse(
                    'scripts:script-generate-demo-encoded',
                    kwargs=dict(pk=self.script.pk)
                ),
                dict(extra_params=params, license_key='0x12345678'),
                format='json'
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_extra_params(self):
        update_script(self.script, extra_params_schema=default_json_schema)
        invalid_extra_params = [
            {},
            None,
            dict(a=1, b=2),
            dict(a=55, b='b2'),
            dict(a=55, b='b4'),
            dict(c=1, d=2),
        ]
        for extra_params in invalid_extra_params:
            response = self.client.post(
                reverse(
                    'scripts:script-generate-demo-encoded',
                    kwargs=dict(pk=self.script.pk)
                ),
                dict(extra_params=extra_params, license_key='0x12345678'),
                format='json'
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_license_key(self):
        valid_license_key = [
            '0x00000000',
            '0x12345678',
            '0xabcdef12',
            '0xABCDEF12',
            'ABCDEF12',
            '87654321',
            '1234-5678-9090-5555',
            'abcd-effe-dcba-1234',
            'ABCD-EFFE-DCBA-1234',
        ]
        for license_key in valid_license_key:
            response = self.client.post(
                reverse(
                    'scripts:script-generate-demo-encoded',
                    kwargs=dict(pk=self.script.pk)
                ),
                dict(license_key=license_key),
                format='json'
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_license_key(self):
        invalid_license_key = [
            {},
            123,
            '0x123456789',
            '123'
            '000-000-000',
            'invalid_key'
        ]
        for license_key in invalid_license_key:
            response = self.client.post(
                reverse(
                    'scripts:script-generate-demo-encoded',
                    kwargs=dict(pk=self.script.pk)
                ),
                dict(license_key=license_key),
                format='json'
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_expiration(self):
        past_dt = date.today() - timedelta(days=1)
        future_dt = date.today() + timedelta(days=10)
        invalid_expiration = [
            {},
            456,
            'some_string',
            '123',
            past_dt.isoformat(),
            future_dt.strftime('%Y.%m.%d')
        ]
        for expires in invalid_expiration:
            response = self.client.post(
                reverse(
                    'scripts:script-generate-demo-encoded',
                    kwargs=dict(pk=self.script.pk)
                ),
                dict(expires=expires, license_key='0x12345678'),
                format='json'
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class GenerateDemoEncodedTests(APITestCase):
    def setUp(self):
        self.user = get_default_user()
        self.client.force_login(self.user)
        self.script = get_default_script()

    def test_valid_response(self):
        response = self.client.post(
            reverse(
                'scripts:script-generate-demo-encoded',
                kwargs=dict(pk=self.script.pk)
            ),
            dict(license_key='0x12345678'),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content_type, 'text/x-python')

    def test_issued_record(self):
        future_dt_str = (date.today() + timedelta(days=10)).isoformat()
        response = self.client.post(
            reverse(
                'scripts:script-generate-demo-encoded',
                kwargs=dict(pk=self.script.pk)
            ),
            dict(
                license_key='0x12345678',
                expires=future_dt_str,
                extra_params=None
            ),
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(reverse('scripts:issued_license-list'))
        self.assertEqual(len(response.data['results']), 1)
        issued = response.data['results'][0]
        self.assertEqual(issued['script'], self.script.pk)
        self.assertEqual(issued['license_key'], '0x12345678')
        self.assertEqual(issued['issued_by'], self.user.username)
        self.assertEqual(issued['issue_type'], 'ENCODED_EXP_LK')
        self.assertEqual(issued['action'], 'GENERATE')
        self.assertEqual(issued['demo_lk'], True)
        self.assertEqual(issued['expires'], future_dt_str)
        self.assertEqual(issued['extra_params'], None)

    def test_force_expiration_for_demo_key(self):
        response = self.client.post(
            reverse(
                'scripts:script-generate-demo-encoded',
                kwargs=dict(pk=self.script.pk)
            ),
            dict(
                license_key='0x12345678',
                expires=None,
                extra_params=None
            ),
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(reverse('scripts:issued_license-list'))
        self.assertEqual(len(response.data['results']), 1)
        issued = response.data['results'][0]
        self.assertIsNotNone(issued['expires'])

    def test_max_expiration_for_demo_key(self):
        future_dt = date.today() + timedelta(
            days=settings.DEMO_KEY_MAX_EXPIRATION_DAYS + 100
        )
        response = self.client.post(
            reverse(
                'scripts:script-generate-demo-encoded',
                kwargs=dict(pk=self.script.pk)
            ),
            dict(
                license_key='0x12345678',
                expires=future_dt.isoformat(),
                extra_params=None
            ),
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(reverse('scripts:issued_license-list'))
        self.assertEqual(len(response.data['results']), 1)
        expires = date.fromisoformat(response.data['results'][0]['expires'])
        self.assertTrue(expires < future_dt)
        self.assertTrue(expires == date.today() + timedelta(
            days=settings.DEMO_KEY_MAX_EXPIRATION_DAYS
        ))
