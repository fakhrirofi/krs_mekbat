from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from war.models import Session, Schedule, UserData
from django.utils import timezone
import json

class AdminAjaxTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(username="admin", password="password")
        self.session = Session.objects.create(
            name="Test Session",
            slug="test-session",
            open_time=timezone.now()
        )
        self.sch1 = Schedule.objects.create(session=self.session, name="Sch1", max_enrolled=10, available=10, group_number=1)
        self.sch2 = Schedule.objects.create(session=self.session, name="Sch2", max_enrolled=5, available=5, group_number=2)
        
        self.user = User.objects.create_user(username="student", password="password")
        self.userdata = UserData.objects.create(user=self.user, nim=12345, name="Student 1")
        
        # Enroll student in Sch1
        self.sch1.add_person(self.userdata, False)

    def test_get_session_data(self):
        self.client.login(username="admin", password="password")
        response = self.client.post(reverse('war:admin_control'), {
            'command': 'get_session_data',
            'session_id': self.session.pk
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['schedules']), 2)
        self.assertEqual(data['schedules'][0]['name'], "Sch1")
        self.assertEqual(len(data['schedules'][0]['students']), 1) # Student 1 is here

    def test_update_schedule_meta(self):
        self.client.login(username="admin", password="password")
        response = self.client.post(reverse('war:admin_control'), {
            'command': 'update_schedule_meta',
            'schedule_id': self.sch1.pk,
            'name': 'Updated Sch1',
            'quota': 20
        })
        self.assertEqual(response.status_code, 200)
        self.sch1.refresh_from_db()
        self.assertEqual(self.sch1.name, 'Updated Sch1')
        self.assertEqual(self.sch1.max_enrolled, 20)
        # Check if available updated correctly (20 - 1 enrolled = 19)
        self.assertEqual(self.sch1.available, 19)

    def test_admin_remove_schedule(self):
        self.client.login(username="admin", password="password")
        
        # Verify enrollment
        self.assertIn(self.sch1, self.userdata.schedules.all())
        
        response = self.client.post(reverse('war:admin_control'), {
            'command': f'admin_remove_schedule:{self.userdata.pk}:{self.sch1.pk}'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        
        self.userdata.refresh_from_db()
        self.assertNotIn(self.sch1, self.userdata.schedules.all())
        self.sch1.refresh_from_db()
        self.assertEqual(self.sch1.available, 10) # Back to full

    def test_admin_change_schedule(self):
        self.client.login(username="admin", password="password")
        
        # Change from Sch1 to Sch2
        response = self.client.post(reverse('war:admin_control'), {
            'command': f'admin_change_schedule:{self.userdata.pk}',
            f'new_schedule_id_{self.userdata.pk}': self.sch2.pk
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        
        # Verify response structure (current_schedules)
        self.assertIn('current_schedules', data)
        self.assertEqual(len(data['current_schedules']), 1)
        self.assertEqual(data['current_schedules'][0]['name'], "Sch2")
        
        self.userdata.refresh_from_db()
        self.assertNotIn(self.sch1, self.userdata.schedules.all())
        self.assertIn(self.sch2, self.userdata.schedules.all())

    def test_empty_schedule(self):
        self.client.login(username="admin", password="password")
        
        response = self.client.post(reverse('war:admin_control'), {
            'command': f'empty_schedule:{self.session.pk}'
        })
        self.assertEqual(response.status_code, 200)
        
        self.sch1.refresh_from_db()
        self.assertEqual(self.sch1.users_enrolled.count(), 0)
        self.assertEqual(self.sch1.available, 10)
