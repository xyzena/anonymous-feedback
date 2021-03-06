from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User, Group

from . import gpg
from .models import Survey, Question, Feedback, PublicKey
from .forms import FeedbackModelForm, RecipientSelectForm, GPGUserCreationForm


TESTUSERKEY = """-----BEGIN PGP PUBLIC KEY BLOCK-----

mQENBFvnIn4BCAC76NouawrjwXPo+/QkzRAiE4PUYbbpKWMzD544rP2hB95OkwHj
IgNC4sHO7E5HndehrftgYlCEaxSAlcednyn+ZlL9TCMqsV4btoAVg2zBVWAL3XfS
+bfKlNlNm93/vde17Ryf9e5LOVs11Jnr2+/CMGS431b/k10ZhTUEAt7FBsuccjyu
DauCnRSFfY3lKDO5tn/yM6fHOF1EEgqZzPFsHjoVPWhgAc5V1IBxj+RbNRke/cJi
JLvsDLOhjMnSNmznwAOAcdmuHM+AOUz5MB/fW4nJ9EKNe5u3+2YjT1yG+XYniDU4
48Y7vikKO0JBE36qcII9d/qd78VRHzmWNsB7ABEBAAG0HlRlc3QgVXNlciA8dGVz
dC51c2VyQGhvc3Qub3JnPokBVAQTAQgAPhYhBM3IHVYBjBeK+d9Gpxj9M173Obys
BQJb5yJ+AhsDBQkNKwuABQsJCAcCBhUKCQgLAgQWAgMBAh4BAheAAAoJEBj9M173
ObysF7sH/0tw0Iqyx7XnHl1OKPEW3YAgy5PD+2XdHszyTylrRS7h4/3wkepEEMEH
rIIFIPAgXyqOz+lb+H5gD4yUryPjYdynoQgZP4tmbp1CsPCXkNfykprLXV3Bv0t9
yJ5+wDEI21dosl+ArOIuwMRieGkrn//cqvpn3A7ftPsrYp8vIIYI0cC9CscziXyX
Z7fw3Yx4GwMJDDThc66MJM65DXR3Gj3bthiFwstqKtK6h3/8XUZ1kqJc39UXw2+g
EXVHXhFzpDGAOi6uLVugp29oQMerFfijFbxPdJZLweZPRXfEie/4at9luVX80sZ8
aDiJiZX64JuxLLj3Adc1zKppAShK/665AQ0EW+cifgEIAJzn5TX6w039UoEr4H7t
nwld/L7W6b4yAoyuLWhKhecloC/AlJx7TQayLfNOHHUxzcIVGvZd0Dn4JCmajRmy
GKhY+c4lJavSP/xSEX2tXF0u+VG71m2AMdKfM4hPmK25AHcrcmxw7SKyelZpD9HW
cj7138B19a83DejmWHqyc0e7OZCt8vDGwiRW9L9tNBxMisPgQBJlt+aV7Vj/Qqwu
CA9ygaEF7tBb6GUxcx6LkhEzCwriGeYI6eF2/wtBmKSyCegl5gXe6ilxDH81clrs
NKsPItPrk/QnQq+bqasHN8uEUjRCNKikIu+gtcla1Y75Rm3+61lIWeAJRY2HRYh2
DhkAEQEAAYkBPAQYAQgAJhYhBM3IHVYBjBeK+d9Gpxj9M173ObysBQJb5yJ+AhsM
BQkNKwuAAAoJEBj9M173Obys82oIAKDc4jUw1H4OuiDrKt/9h4awpIlc5fPM9Su6
dr9SeW6j8swX+M+6FU6MnofHtg2zDPhJoT/Z7GHnqCeMuWP5fmh0EwnLFPLbin8m
9e5DmTrobMibrSvS0+qqExosJl2nxxx86dwZfGpw7flTj30YDeC9Z3t3/DssbiSc
QzSiaQqb9G4e0p2vgeyuvKaSNMA2aNl3u3qJePnf1eeYHzAQLJGF3q7Sk5+wcAca
SlDrV7OGPGAZmlTzxKzvuoPfovA1BqHtypdoPyE+fe/4jOBs5bSIrbhcauk7FT3y
Ys3EtS5yqCxqAu8T8JlGIbqYL6g1RMPbPuO5Hr3+k30kFx68oeg=
=3CxF
-----END PGP PUBLIC KEY BLOCK-----"""

TESTUSERFP = "CDC81D56018C178AF9DF46A718FD335EF739BCAC"


class TestPublicKey(TestCase):

    def test_bad_key(self):
        """
        A ValueError should be raised if the key text is not valid
        """
        badkeytext = "Surely this is not a valid key."
        publickey = PublicKey()
        with self.assertRaises(ValueError):
            publickey.import_to_gpg(ascii_key=badkeytext)

    def test_import_to_gpg(self):
        """Test import of a proper key"""
        gpg.delete_keys(TESTUSERFP) # remove the test key
        # the key should not yet be installed
        self.assertFalse(gpg.list_keys(keys=TESTUSERFP))
        publickey = PublicKey()
        publickey.import_to_gpg(ascii_key=TESTUSERKEY)
        self.assertEqual(publickey.fingerprint, TESTUSERFP)
        # the key should now be installed
        self.assertTrue(gpg.list_keys(keys=TESTUSERFP))

    def test_key_already_imported(self):
        """Test import of a key already in gpg"""
        gpg.import_keys(TESTUSERKEY)
        self.assertTrue(gpg.list_keys(keys=TESTUSERFP))
        publickey = PublicKey()
        publickey.import_to_gpg(ascii_key=TESTUSERKEY)
        self.assertEqual(publickey.fingerprint, TESTUSERFP)
        # the key should still be installed
        self.assertTrue(gpg.list_keys(keys=TESTUSERFP))

    def test_get_uid(self):
        """Make sure get_uid() works whether key is imported or not"""
        testkey = PublicKey()
        self.assertEqual(testkey.get_uid(), '')
        testkey.import_to_gpg(ascii_key=TESTUSERKEY)
        self.assertEqual(testkey.get_uid(), 'Test User <test.user@host.org>')

    def test_get_user_data(self):
        """Make sure get_user_data() works whether key is imported or not"""
        testkey = PublicKey()
        self.assertEqual(testkey.get_user_data(),
                         {"first_name": '', "last_name": '', "email": ''})
        testkey.import_to_gpg(ascii_key=TESTUSERKEY)
        self.assertEqual(testkey.get_user_data(),
                         {"first_name": 'Test',
                          "last_name": 'User',
                          "email": 'test.user@host.org'})


class TestIndexView(TestCase):

    def setUp(self):
        # ResultsView requires a logged in user
        self.testuser, flag = User.objects.get_or_create(username='testuser')
        self.assertTrue(flag)
        self.client.force_login(self.testuser)

    def test_unpublished_survey(self):
        """Unpublished survey should not be in queryset"""
        future = timezone.now() + timezone.timedelta(hours=1)
        past = timezone.now() - timezone.timedelta(hours=1)
        Survey.objects.create(title="Past Survey", pub_date=past)
        Survey.objects.create(title="Future Survey", pub_date=future)
        url = reverse('surveys:index')
        response = self.client.get(url)
        self.assertQuerysetEqual(response.context['survey_list'],
                                 ['<Survey: Past Survey>'])

    def test_logged_out(self):
        """If user logged out, should get redirected"""
        self.client.logout()
        url = reverse('surveys:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)


class TestResultsView(TestCase):

    def setUp(self):
        # ResultsView requires a logged in user
        self.testuser, flag = User.objects.get_or_create(username='testuser')
        self.assertTrue(flag)
        self.client.force_login(self.testuser)

    def test_no_survey(self):
        """"If no survey, should get a 404"""
        url = reverse('surveys:results', args=(20,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_no_results(self):
        """"If no results, an appropriate message is displayed"""
        s = Survey.objects.create(title="Test Survey",
                                  pub_date=timezone.now(),
                                  results_published=True)
        url = reverse('surveys:results', args=(1,))
        response = self.client.get(url)
        self.assertContains(response, "No results are available.")

    def test_results_filtered_by_survey(self):
        """Results page should only show results for given survey"""
        s = Survey.objects.create(title="Test Survey",
                                  pub_date=timezone.now(),
                                  results_published=True)
        q = Question.objects.create(survey=s, question_text="Q1")
        f = Feedback.objects.create(recipient=self.testuser,
                                    author=self.testuser,
                                    question=q,
                                    feedback_text="meh")
        url = reverse('surveys:results', args=(1,))
        response = self.client.get(url)
        self.assertQuerysetEqual(
            response.context['feedback_list'],
            ['<Feedback: Private feedback for testuser>']
        )
        # now increment the URL pk, there should be no results here
        # even though a Survey 2 exists
        Survey.objects.create(title="Test Survey 2",
                              pub_date=timezone.now(),
                              results_published=True)
        url = reverse('surveys:results', args=(2,))
        response = self.client.get(url)
        self.assertContains(response, "No results are available.")
        self.assertQuerysetEqual(response.context['feedback_list'], [])

    def test_unpublished_results(self):
        """Make sure no results in QuerySet if not results_published"""
        s = Survey.objects.create(title="Test Survey",
                                  pub_date=timezone.now(),
                                  results_published=False)
        q = Question.objects.create(survey=s, question_text="Q1")
        f = Feedback.objects.create(recipient=self.testuser,
                                    author=self.testuser,
                                    question=q,
                                    feedback_text="meh")
        url = reverse('surveys:results', args=(1,))
        response = self.client.get(url)
        self.assertQuerysetEqual(response.context['feedback_list'], [])
        self.assertContains(response, "not yet published.")

        s.results_published = True
        s.save()
        url = reverse('surveys:results', args=(1,))
        response = self.client.get(url)
        self.assertQuerysetEqual(
            response.context['feedback_list'],
            ['<Feedback: Private feedback for testuser>']
        )

    def test_logged_out(self):
        """If user logged out, should get redirected"""
        self.client.logout()
        url = reverse('surveys:results', args=(1,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)


class TestGPGUserCreationForm(TestCase):

    def setUp(self):
        self.form = GPGUserCreationForm(data={'username': 'testuser',
                                              'password1': 'socomplicated',
                                              'password2': 'socomplicated',
                                              'public_key': TESTUSERKEY})

    def test_valid_key(self):
        self.assertTrue(self.form.is_valid())

    def test_key_attached(self):
        user = self.form.save()
        self.assertEqual(user.publickey.fingerprint, TESTUSERFP)

    def test_user_data_extracted(self):
        user = self.form.save()
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")
        self.assertEqual(user.email, 'test.user@host.org')

    def test_duplicate_public_key(self):
        user = self.form.save()
        data = self.form.data
        another = GPGUserCreationForm(data=data)
        self.assertFalse(another.is_valid())


class TestSignupView(TestCase):

    def test_user_creation(self):
        user_count = User.objects.count()
        url = reverse('surveys:signup')
        uname = "runkle"
        response = self.client.post(url, {'username': uname,
                                          'password1': "holyguacamole", 
                                          'password2': "holyguacamole", 
                                          'public_key': TESTUSERKEY})
        self.assertEqual(User.objects.count(), user_count + 1)
        newuser = User.objects.get(username=uname)
        self.assertEqual(newuser.publickey.fingerprint,
                         TESTUSERFP)
        self.assertEqual(newuser.get_full_name(), "Test User")
        self.assertEqual(newuser.email, "test.user@host.org")


class TestFeedbackModelForm(TestCase):
    
    def setUp(self):
        # this TestCase requires a user with publickey
        self.testuser, flag = User.objects.get_or_create(username='testuser')
        self.assertTrue(flag)
        self.testuser.publickey = PublicKey(user=self.testuser)
        self.testuser.publickey.import_to_gpg(TESTUSERKEY)

    def test_encryption(self):
        q = Question(question_text="Why")
        f = Feedback(question=q, recipient=self.testuser)
        raw_ans = "Just because"
        form = FeedbackModelForm(question=q,
                                 instance=f,
                                 data={'feedback_text': raw_ans})
        self.assertTrue(form.is_valid())
        self.assertIn("-----BEGIN PGP MESSAGE-----",
                      form.cleaned_data["feedback_text"])
        self.assertNotIn(raw_ans, form.cleaned_data["feedback_text"])


class TestRecipientSelectForm(TestCase):

    def test_non_recipients_not_in_dropdown(self):
        recipient, _ = User.objects.get_or_create(username='recipient')
        rgroup, _ = Group.objects.get_or_create(name='Feedback Recipients')
        recipient.groups.add(rgroup)
        nonrecipient, _ = User.objects.get_or_create(username='nonrecipient')

        form = RecipientSelectForm()
        self.assertIn(recipient, form.fields["user"].choices.queryset)
        self.assertNotIn(nonrecipient, form.fields["user"].choices.queryset)
