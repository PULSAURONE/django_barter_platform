# ads/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Ad, ExchangeProposal


class AdModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.ad = Ad.objects.create(
            title="Тестовый обмен",
            description="Описание тестового обмена",
            category="Электроника",
            condition="new",
            user=self.user
        )

    def test_ad_creation(self):
        self.assertEqual(self.ad.title, "Тестовый обмен")
        self.assertEqual(self.ad.user.username, "testuser")
        self.assertEqual(Ad.objects.count(), 1)


class AdViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')

        self.client.login(username='user1', password='password123')

        self.ad1 = Ad.objects.create(
            title="Тестовый вид user1",
            description="Описание",
            category="Книги",
            condition="used",
            user=self.user1
        )
        self.ad2 = Ad.objects.create(
            title="Поисковый запрос",
            description="Уникальное описание",
            category="Электроника",
            condition="new",
            user=self.user2
        )

    def test_ad_list_view(self):
        response = self.client.get(reverse('ad_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Тестовый вид user1")
        self.assertTemplateUsed(response, 'ads/ad_list.html')

    def test_ad_list_view_with_filters(self):
        # Тест поиска по заголовку
        response = self.client.get(reverse('ad_list') + '?q=Поисковый')
        self.assertContains(response, "Поисковый запрос")
        self.assertNotContains(response, "Тестовый вид user1")

        # Тест фильтра по категории
        response = self.client.get(reverse('ad_list') + '?category=Книги')
        self.assertContains(response, "Тестовый вид user1")
        self.assertNotContains(response, "Поисковый запрос")

    def test_ad_detail_view(self):
        response = self.client.get(reverse('ad_detail', args=[self.ad1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Тестовый вид user1")

    def test_ad_create_view(self):
        ads_count = Ad.objects.count()
        response = self.client.post(reverse('ad_create'), {
            'title': 'Новое объявление',
            'description': 'Супер вещь',
            'category': 'Одежда',
            'condition': 'new'
        })
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertEqual(Ad.objects.count(), ads_count + 1)
        self.assertTrue(Ad.objects.filter(title='Новое объявление').exists())

    def test_ad_update_permission(self):
        response = self.client.get(reverse('ad_update', args=[self.ad1.id]))
        self.assertEqual(response.status_code, 200)

        self.client.login(username='user2', password='password123')
        response = self.client.get(reverse('ad_update', args=[self.ad1.id]))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_ad_delete_permission(self):
        self.client.login(username='user2', password='password123')
        response = self.client.post(reverse('ad_delete', args=[self.ad1.id]))
        self.assertEqual(response.status_code, 403)  # Forbidden
        self.assertTrue(Ad.objects.filter(pk=self.ad1.id).exists())  # Объявление не удалено

        self.client.login(username='user1', password='password123')
        response = self.client.post(reverse('ad_delete', args=[self.ad1.id]))
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertFalse(Ad.objects.filter(pk=self.ad1.id).exists())  # Объявление удалено


class ExchangeProposalTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')

        self.ad1 = Ad.objects.create(title="Лыжи user1", category="Спорт", condition="used", user=self.user1)
        self.ad2 = Ad.objects.create(title="Книга user2", category="Книги", condition="new", user=self.user2)

    def test_proposal_creation(self):
        self.client.login(username='user1', password='password123')
        response = self.client.post(
            reverse('proposal_create', kwargs={'ad_receiver_id': self.ad2.pk}),
            {'ad_sender': self.ad1.pk, 'comment': 'Давай меняться!'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ExchangeProposal.objects.exists())
        proposal = ExchangeProposal.objects.first()
        self.assertEqual(proposal.status, 'pending')
        self.assertEqual(proposal.ad_sender, self.ad1)
        self.assertEqual(proposal.ad_receiver, self.ad2)

    def test_proposal_status_update(self):
        proposal = ExchangeProposal.objects.create(ad_sender=self.ad1, ad_receiver=self.ad2)

        self.client.login(username='user2', password='password123')
        response = self.client.get(reverse('proposal_update_status', kwargs={'pk': proposal.pk, 'status': 'accepted'}),
                                   follow=True)

        self.assertEqual(response.status_code, 200)  # После редиректа на proposal_list
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, 'accepted')

    def test_proposal_status_update_permission(self):
        proposal = ExchangeProposal.objects.create(ad_sender=self.ad1, ad_receiver=self.ad2)

        # Логинимся как отправитель (user1) и пытаемся принять свое же предложение
        self.client.login(username='user1', password='password123')
        self.client.get(reverse('proposal_update_status', kwargs={'pk': proposal.pk, 'status': 'accepted'}))

        proposal.refresh_from_db()
        self.assertEqual(proposal.status, 'pending')

    def test_cannot_propose_to_self(self):
        self.client.login(username='user1', password='password123')
        ad_of_user1_as_receiver = Ad.objects.create(title="Второе объявление user1", category="Прочее", condition="new",
                                                    user=self.user1)

        response = self.client.post(
            reverse('proposal_create', kwargs={'ad_receiver_id': ad_of_user1_as_receiver.pk}),
            {'ad_sender': self.ad1.pk, 'comment': 'Обмен с самим собой'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Вы не можете предложить обмен на свое собственное объявление.")
        self.assertEqual(ExchangeProposal.objects.count(), 0)