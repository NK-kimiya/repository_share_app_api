from django.contrib import admin
from .models import User,Room,Repository,Category,GitProject,Message,FavoriteRepository
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _

'''
カスタムユーザーモデルを適切に表示・管理するための設定
'''
class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'username']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('username',)}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )
admin.site.register(User,UserAdmin)
admin.site.register(Room)
admin.site.register(Repository)
admin.site.register(Category)
admin.site.register(GitProject)
admin.site.register(Message)
admin.site.register(FavoriteRepository)

#管理ユーザー
'''
superuser@gmail.com
super
'''

'''
superuser2@gmail.com
super2
'''

'''
superuser3@gmail.com
super3
'''

'''
super4@gmail.com
super4
super4
'''

'''
kinarishige26@gmail.com
キミコウ
nari71821955
'''

#ルームパスワード
'''
teamhina
'''

'''
ハッカソン大好き
password123
'''
