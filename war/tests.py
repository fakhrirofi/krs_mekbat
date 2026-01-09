from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Session, Schedule, AdminControl, UserData

class AdminControlTestCase(TestCase):
    def test_admin_control_creation(self):
        control = AdminControl.objects.create(name="register", active=True)
        self.assertEqual(str(control), "register")
        self.assertTrue(control.active)

class SessionTestCase(TestCase):
    def setUp(self):
        self.session = Session.objects.create(
            name="Test Session",
            slug="test-session",
            open_time=timezone.now()
        )

    def test_session_creation(self):
        self.assertEqual(self.session.name, "Test Session")
        self.assertTrue(self.session.active)

class ScheduleTestCase(TestCase):
    def setUp(self):
        self.session = Session.objects.create(
            name="Test Session",
            slug="test-session",
            open_time=timezone.now()
        )
        self.user = User.objects.create_user(username="123", password="password")
        self.userdata = UserData.objects.create(
            user=self.user,
            nim=123,
            name="Test User",
            handphone="08123"
        )
        self.schedule = Schedule.objects.create(
            session=self.session,
            name="Monday 7.00",
            group_number=1,
            max_enrolled=1
        )

    def test_add_person_success(self):
        result = self.schedule.add_person(self.userdata, changed=False)
        self.assertEqual(result, "success")
        self.assertEqual(self.schedule.users_enrolled.count(), 1)
        self.assertEqual(self.schedule.available, 0)

    def test_add_person_limit(self):
        # Fill the schedule
        self.schedule.add_person(self.userdata, changed=False)
        
        # Create another user
        user2 = User.objects.create_user(username="456", password="password")
        userdata2 = UserData.objects.create(
            user=user2,
            nim=456,
            name="Test User 2",
            handphone="08123"
        )
        
        result = self.schedule.add_person(userdata2, changed=False)
        self.assertEqual(result, "limit")
        self.assertEqual(self.schedule.users_enrolled.count(), 1)


class ViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="123", password="password")
        self.admin = User.objects.create_superuser(username="admin", password="password")
        self.userdata = UserData.objects.create(
            user=self.user,
            nim=123,
            name="Test User",
            handphone="08123"
        )
        UserData.objects.create(
            user=self.admin,
            nim=999,
            name="Admin User",
            handphone="000"
        )
        
        # Ensure 'register' control exists
        AdminControl.objects.create(name="register", active=True)

    def test_login_view_context(self):
        response = self.client.get(reverse('war:login'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['register_on'])
        self.assertTrue(response.context['register_on'].active)
        
        # Test inactive
        ctrl = AdminControl.objects.get(name="register")
        ctrl.active = False
        ctrl.save()
        
        response = self.client.get(reverse('war:login'))
        self.assertFalse(response.context['register_on'].active)

    def test_home_view_redirect(self):
        # Without login
        response = self.client.get(reverse('war:home'))
        self.assertNotEqual(response.status_code, 200) # Should redirect

    def test_home_view_access(self):
        self.client.login(username="123", password="password")
        response = self.client.get(reverse('war:home'))
        self.assertEqual(response.status_code, 200)

    def test_admin_control_forbidden_for_user(self):
        self.client.login(username="123", password="password")
        response = self.client.get(reverse('war:admin_control'))
        self.assertEqual(response.status_code, 302) # Redirects to home

    def test_admin_control_access_for_admin(self):
        self.client.login(username="admin", password="password")
        response = self.client.get(reverse('war:admin_control'))
        self.assertEqual(response.status_code, 200)

    def test_admin_create_session(self):
        self.client.login(username="admin", password="password")
        response = self.client.post(reverse('war:admin_control'), {
            'command': 'create_session',
            'session_name': 'New Session',
            'session_slug': 'new-session',
            'session_open_time': '2024-01-01T10:00'
        })
        self.assertTrue(Session.objects.filter(slug='new-session').exists())

    def test_admin_move_student_command(self):
        self.client.login(username="admin", password="password")
        
        session = Session.objects.create(
            name="Test Session",
            slug="test-session",
            open_time=timezone.now()
        )
        
        sch1 = Schedule.objects.create(session=session, name="Sch1", max_enrolled=5, available=5, group_number=1)
        sch2 = Schedule.objects.create(session=session, name="Sch2", max_enrolled=5, available=5, group_number=2)
        
        # Add to Sch1
        sch1.add_person(self.userdata, False)
        self.assertIn(sch1, self.userdata.schedules.all())
        
        # Move to Sch2 via command
        response = self.client.post(reverse('war:admin_control'), {
            'command': 'move_student',
            'user_id': self.userdata.pk,
            'target_schedule_id': sch2.pk,
            # csrf handled by client automatically?
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'success'})
        
        # Verify
        self.userdata.refresh_from_db()
        sch1.refresh_from_db()
        sch2.refresh_from_db()
        
        self.assertNotIn(sch1, self.userdata.schedules.all())
        self.assertIn(sch2, self.userdata.schedules.all())
        self.assertEqual(sch1.available, 5) # Back to full (was 4 after add_person)
        self.assertEqual(sch2.available, 4) # Decreased


