# ads/views.py
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from .models import Ad, ExchangeProposal
from .forms import AdForm, ExchangeProposalForm


# 1. Отображение списка объявлений (с поиском и фильтрацией)
class AdListView(ListView):
    model = Ad
    template_name = 'ads/ad_list.html'
    context_object_name = 'ads'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        category = self.request.GET.get('category')
        condition = self.request.GET.get('condition')

        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(description__icontains=query))
        if category:
            queryset = queryset.filter(category__iexact=category)
        if condition:
            queryset = queryset.filter(condition__iexact=condition)

        return queryset


# 2. Детальное отображение объявления
class AdDetailView(DetailView):
    model = Ad
    template_name = 'ads/ad_detail.html'


# 3. Создание объявления
class AdCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Ad
    form_class = AdForm
    template_name = 'ads/ad_form.html'
    success_url = reverse_lazy('ad_list')
    success_message = "Объявление '%(title)s' успешно создано!"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


# 4. Редактирование объявления
class AdUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Ad
    form_class = AdForm
    template_name = 'ads/ad_form.html'
    success_url = reverse_lazy('ad_list')
    success_message = "Объявление '%(title)s' успешно обновлено!"

    def test_func(self):
        ad = self.get_object()
        return self.request.user == ad.user


# 5. Удаление объявления
class AdDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Ad
    template_name = 'ads/ad_confirm_delete.html'
    success_url = reverse_lazy('ad_list')
    success_message = "Объявление успешно удалено!"

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

    def test_func(self):
        ad = self.get_object()
        return self.request.user == ad.user


# 6. Создание предложения обмена
class ProposalCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = ExchangeProposal
    form_class = ExchangeProposalForm
    template_name = 'ads/proposal_form.html'
    success_url = reverse_lazy('proposal_list')
    success_message = "Предложение обмена успешно отправлено!"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ad_receiver'] = get_object_or_404(Ad, pk=self.kwargs['ad_receiver_id'])
        return context

    def form_valid(self, form):
        ad_receiver = get_object_or_404(Ad, pk=self.kwargs['ad_receiver_id'])
        form.instance.ad_receiver = ad_receiver

        if form.instance.ad_sender.user == ad_receiver.user:
            form.add_error(None, "Вы не можете предложить обмен на свое собственное объявление.")
            return self.form_invalid(form)

        return super().form_valid(form)


# 7.  предложения
class ProposalListView(LoginRequiredMixin, ListView):
    model = ExchangeProposal
    template_name = 'ads/proposal_list.html'

    def get_queryset(self):
        user = self.request.user
        return ExchangeProposal.objects.filter(
            Q(ad_sender__user=user) | Q(ad_receiver__user=user)
        ).select_related('ad_sender__user', 'ad_receiver__user').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        all_proposals = context['object_list']

        # Разделяем общий список на два: входящие и исходящие
        context['incoming_proposals'] = [p for p in all_proposals if p.ad_receiver.user == user]
        context['outgoing_proposals'] = [p for p in all_proposals if p.ad_sender.user == user]

        return context


# Обновление статуса предложения
def update_proposal_status(request, pk, status):
    proposal = get_object_or_404(ExchangeProposal, pk=pk)

    if request.user == proposal.ad_receiver.user and status in ['accepted', 'rejected']:
        proposal.status = status
        proposal.save()
        messages.success(request, f"Статус предложения изменен на '{proposal.get_status_display()}'.")
    else:
        messages.error(request, "У вас нет прав для выполнения этого действия.")

    return redirect('proposal_list')