from .forms import QuestionsSearchForm

def search_form(request):
  # 全画面で利用できる検索フォーム
  return {'qsearchform':QuestionsSearchForm(request.GET or None)}