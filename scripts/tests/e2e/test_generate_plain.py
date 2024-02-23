import json

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


class GeneratePlainPermissionsTests(APITestCase):
    def setUp(self):
        self.user = get_default_user()
        self.client.force_login(self.user)
        self.script = get_default_script()

    def test_not_authorized_user(self):
        self.client.logout()
        response = self.client.post(reverse(
            'scripts:script-generate-plain',
            kwargs=dict(pk=self.script.id)
        ))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_downloadable_script_wo_force_perms(self):
        not_downloadable = [
            dict(is_active=False, enabled=True),
            dict(is_active=True, enabled=False),
            dict(is_active=False, enabled=False),
        ]
        for params in not_downloadable:
            update_script(self.script, **params)
            response = self.client.post(reverse(
                'scripts:script-generate-plain',
                kwargs=dict(pk=self.script.id)
            ))
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_downloadable_script_w_force_perms(self):
        give_permission_to_user(self.user, 'force_issue_plain_script')

        not_downloadable = [
            dict(is_active=False, enabled=True),
            dict(is_active=True, enabled=False),
            dict(is_active=False, enabled=False),
        ]
        for params in not_downloadable:
            update_script(self.script, **params)
            response = self.client.post(reverse(
                'scripts:script-generate-plain',
                kwargs=dict(pk=self.script.id)
            ))
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_script_not_allowing_plain_issue_wo_force_perms(self):
        update_script(self.script, allow_issue_plain=False)
        response = self.client.post(reverse(
            'scripts:script-generate-plain',
            kwargs=dict(pk=self.script.id)
        ))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_script_not_allowing_plain_issue_w_force_perms(self):
        give_permission_to_user(self.user, 'force_issue_plain_script')
        update_script(self.script, allow_issue_plain=False)
        response = self.client.post(reverse(
            'scripts:script-generate-plain',
            kwargs=dict(pk=self.script.id)
        ))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_script_allowing_plain_issue_wo_force_perms(self):
        response = self.client.post(reverse(
            'scripts:script-generate-plain',
            kwargs=dict(pk=self.script.id)
        ))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_script_allowing_plain_issue_w_force_perms(self):
        give_permission_to_user(self.user, 'force_issue_plain_script')
        response = self.client.post(reverse(
            'scripts:script-generate-plain',
            kwargs=dict(pk=self.script.id)
        ))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GeneratePlainValidationTests(APITestCase):
    def setUp(self):
        self.user = get_default_user()
        self.client.force_login(self.user)
        self.script = get_default_script()

    def test_not_existing_script(self):
        response = self.client.post(reverse(
            'scripts:script-generate-plain',
            kwargs=dict(pk='not_existing_script')
        ))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_empty_request(self):
        response = self.client.post(
            reverse(
                'scripts:script-generate-plain',
                kwargs=dict(pk=self.script.pk)
            ),
            dict()
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
                    'scripts:script-generate-plain',
                    kwargs=dict(pk=self.script.pk)
                ),
                dict(extra_params=params),
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
                    'scripts:script-generate-plain',
                    kwargs=dict(pk=self.script.pk)
                ),
                dict(extra_params=params),
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
                    'scripts:script-generate-plain',
                    kwargs=dict(pk=self.script.pk)
                ),
                dict(extra_params=extra_params),
                format='json'
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class GeneratePlainTests(APITestCase):
    def setUp(self):
        self.user = get_default_user()
        self.client.force_login(self.user)
        self.script = get_default_script()

    def test_valid_response(self):
        response = self.client.post(
            reverse(
                'scripts:script-generate-plain',
                kwargs=dict(pk=self.script.pk)
            ),
            dict(),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content_type, 'text/x-python')

    def test_issued_record(self):
        response = self.client.post(
            reverse(
                'scripts:script-generate-plain',
                kwargs=dict(pk=self.script.pk)
            ),
            dict(),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(reverse('scripts:issued_license-list'))
        self.assertEqual(len(response.data['results']), 1)
        issued = response.data['results'][0]
        self.assertEqual(issued['script'], self.script.pk)
        self.assertEqual(issued['license_key'], None)
        self.assertEqual(issued['issued_by'], self.user.username)
        self.assertEqual(issued['issue_type'], 'PLAIN')
        self.assertEqual(issued['action'], 'GENERATE')
        self.assertEqual(issued['demo_lk'], False)
        self.assertEqual(issued['expires'], None)
        self.assertEqual(issued['extra_params'], None)
