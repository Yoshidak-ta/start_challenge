from .forms import QuestionsSearchForm

def search_form(request):
  # 全画面で利用できる検索フォーム
  return {'qsearchform':QuestionsSearchForm(request.GET or None)}

# 通知チェック
def notification_flag(request):
  return {
    'show_notification': getattr(request, 'show_notification', False)
  }