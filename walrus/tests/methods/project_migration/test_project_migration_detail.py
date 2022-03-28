from methods.regular.regular_api import *
from walrus.tests.test_utils import testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from base64 import b64encode
from methods.project_migration.project_migration_detail import project_migration_detail_core

class TestProjectMigrationDetail(testing_setup.DiffgramBaseTestCase):
    """

    """

    def setUp(self):
        # TODO: this test is assuming the 'my-sandbox-project' exists and some object have been previously created.
        # For future tests a mechanism of setting up and tearing down the database should be created.
        super(TestProjectMigrationDetail, self).setUp()
        project_data = data_mocking.create_project_with_context(
            {
                'users': [
                    {'username': 'Test',
                     'email': 'test@test.com',
                     'password': 'diffgram123',
                     }
                ]
            },
            self.session
        )
        self.project = project_data['project']
        self.project_data = project_data
        self.auth_api = common_actions.create_project_auth(project = self.project,
                                                           session = self.session,
                                                           role = "admin")
        self.member = self.auth_api.member

    def test_api_project_migration_detail(self):
        project_migration = data_mocking.create_project_migration({
            'status': 'testing',
            'member_created_id': self.member.id,
            'project_id': self.project.id
        }, self.session)
        auth_api = common_actions.create_project_auth(project = self.project, session = self.session, role = "admin")
        credentials = b64encode(f"{auth_api.client_id}:{auth_api.client_secret}".encode()).decode('utf-8')
        with self.client.session_transaction() as session:
            endpoint = f"/api/walrus/project/{self.project.project_string_id}/project-migration/detail/{project_migration.id}"
        response = self.client.get(
            endpoint,
            data = {},
            headers = {
                'directory_id': str(self.project.directory_default_id),
                'Authorization': f"Basic {credentials}"
            }
        )
        data = response.json
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['id'], project_migration.id)
        self.assertEqual(data['status'], project_migration.status)
        self.assertEqual(data['connection_id'], project_migration.connection_id)
        self.assertEqual(data['member_created_id'], self.member.id)

    def test_project_migration_detail_core(self):
        project_migration = data_mocking.create_project_migration({
            'status': 'testing',
            'member_created_id': self.member.id,
            'project_id': self.project.id
        }, self.session)
        data, log = project_migration_detail_core(
            session = self.session,
            project_string_id = self.project.project_string_id,
            project_migration_id = project_migration.id,
            member = self.member,
            log = regular_log.default()
        )
        self.assertEqual(len(log['error'].keys()), 0)
        self.assertEqual(data['id'], project_migration.id)
        self.assertEqual(data['status'], project_migration.status)
        self.assertEqual(data['connection_id'], project_migration.connection_id)
        self.assertEqual(data['member_created_id'], self.member.id)
