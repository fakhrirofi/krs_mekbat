from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from war.models import Session, Schedule, AdminControl
from django.utils import timezone

class AdminFeaturesTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(username="admin", password="password")
        self.session = Session.objects.create(
            name="Test Session",
            slug="test-session",
            open_time=timezone.now()
        )
        AdminControl.objects.create(name="register", active=True)

    def test_toggle_session(self):
        self.client.login(username="admin", password="password")
        self.assertTrue(self.session.active)
        
        response = self.client.post(reverse('war:admin_control'), {
            'command': f'toggle_session:{self.session.slug}'
            # No selection needed primarily
        })
        self.session.refresh_from_db()
        self.assertFalse(self.session.active)

    def test_accept_schedule_with_quota(self):
        self.client.login(username="admin", password="password")
        
        # New structure: days, final_times, quotas
        response = self.client.post(reverse('war:admin_control'), {
            'command': 'accept_schedule',
            'target_session_slug': self.session.slug,
            'days': ['Senin', 'Rabu'],
            'final_times': ['07.00 - 09.00', '10.00 - 12.00'],
            'quotas': ['50', '25']
        })
        
        # Verify count: 2 schedules * 1 groups = 2 items
        self.assertEqual(Schedule.objects.filter(session=self.session).count(), 2)
        
        # Verify specific schedule properties
        sch1 = Schedule.objects.filter(name="Senin 07.00 - 09.00").first()
        self.assertIsNotNone(sch1)
        self.assertEqual(sch1.max_enrolled, 50)
        self.assertEqual(sch1.available, 50) # Should initialized to max

        sch2 = Schedule.objects.filter(name="Rabu 10.00 - 12.00").first()
        self.assertIsNotNone(sch2)
        self.assertEqual(sch2.max_enrolled, 25)

    def test_create_session_auto_slug(self):
        self.client.login(username="admin", password="password")
        
        response = self.client.post(reverse('war:admin_control'), {
            'command': 'create_session',
            'session_name': 'My New Session',
            'session_open_time': '2025-01-01T08:00'
            # No slug provided
        })
        
        # Check if slugified
        self.assertTrue(Session.objects.filter(slug='my-new-session').exists())

    def test_delete_session_inline(self):
         self.client.login(username="admin", password="password")
         new_ses = Session.objects.create(name="Delete Me", slug="delete-me", open_time=timezone.now())
         
         response = self.client.post(reverse('war:admin_control'), {
             'command': f'delete_session:{new_ses.id}'
         })
         
         self.assertFalse(Session.objects.filter(name="Delete Me").exists())

    def test_admin_reset_password_ajax(self):
        self.client.login(username="admin", password="password")
        # Removed password change to prevent session invalidation
        
        response = self.client.post(
            reverse('war:admin_control'),
            {
                'command': f'admin_reset_password:{self.admin.id}',
                f'new_password_{self.admin.id}': 'ajaxpassword123'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        
        u = User.objects.get(pk=self.admin.id)
        self.assertTrue(u.check_password('ajaxpassword123'))
