from django.views import generic
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.utils import timezone

from .models import Survey, Feedback
from .forms import FeedbackModelForm, RecipientSelectForm, GPGUserCreationForm


RECIPIENTS_GROUP = Group.objects.get_or_create(name="Feedback Recipients")[0]
AUTHORS_GROUP = Group.objects.get_or_create(name="Feedback Authors")[0]


class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'surveys/index.html'
    def get_queryset(self):
        """Return published Surveys"""
        now = timezone.now()
        return Survey.objects.filter(pub_date__lt=now).order_by('pub_date')


@login_required
def form_fill(request, pk):
    survey = get_object_or_404(Survey, pk=pk)
    if request.method == 'POST':
        userform = RecipientSelectForm(request.POST)
        # todo replace the ugly assert below.
        # the call to is_valid creates userform.cleaned_data
        assert(userform.is_valid())
        recipient = userform.cleaned_data['user']
        forms = [FeedbackModelForm(request.POST,
                                   question=q,
                                   instance=Feedback(recipient=recipient,
                                                     author=request.user,
                                                     question=q),
                                   prefix=("question%s" % q.id))
                 for q in survey.question_set.all()]
        if all(form.is_valid() for form in forms):
            # do something with the cleaned data
            for form in forms:
                form.save()
            return HttpResponseRedirect('surveys/../submitted/')
    else:
        userform = RecipientSelectForm()
        forms = [FeedbackModelForm(question=q,
                                   prefix=("question%s" % q.id))
                 for q in survey.question_set.all()]
    return render(request, 'surveys/form_fill.html',
                  {'forms': forms, 'userform': userform, 'survey': survey})


class SubmittedView(generic.DetailView):
    model = Survey
    template_name = 'surveys/submitted.html'


class ResultsView(LoginRequiredMixin, generic.ListView):

    template_name = 'surveys/results.html'

    def get_queryset(self):
        """Return feedback for this user"""
        survey = get_object_or_404(Survey, pk=self.kwargs['pk'])
        if not survey.results_published:
            return Feedback.objects.none()
        questions = survey.question_set.all()
        return Feedback.objects.filter(recipient=self.request.user,
                                       question__in=questions)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['survey'] = get_object_or_404(Survey, pk=self.kwargs['pk'])
        return context


def signup(request):
    if request.method == 'POST':
        form = GPGUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # add users to default groups
            user.groups.add(RECIPIENTS_GROUP)
            user.groups.add(AUTHORS_GROUP)
            user.save()
            return redirect('../../accounts/login/?newuser=%s' %
                            user.get_username())
    else:
        form = GPGUserCreationForm()
    return render(request, 'surveys/signup.html', {'form': form})
