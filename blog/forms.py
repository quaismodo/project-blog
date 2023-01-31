# импортируем модуль forms для работы с формами
from django import forms
from .models import Comment

# Форма наследуется от базового класса Form,
# которая позволяет создавать стандартные формы,
# определяя поля и проверки
class EmailPostForm(forms.Form):
    # поле name используется для имя отправителя сообщения
    name = forms.CharField(max_length=25) # CharField отображается как <input type="text">
    email = forms.EmailField()
    to = forms.EmailField()
    # поле comments не обязательно для заполнения и использует виджет textarea
    comments = forms.CharField(required=False, widget=forms.Textarea) # переобределяем виджет на <textarea>

class CommentForm(forms.ModelForm):
    # создание класса формы для комментариев, с использованием ModelForm
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']

class SearchForm(forms.Form):
    query = forms.CharField()