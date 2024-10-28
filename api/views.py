# # myapp/views.py

# from django.http import JsonResponse
# from .tasks import add

# def add_view(request):
#     # Gọi task
#     result = add.delay(4, 6)
#     while(result.ready() is False):
#         pass
#     return JsonResponse({'task_id': result.id, 'status': result.result})
