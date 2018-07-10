# {% if '%publish_announcement%' in permissions %}
#     {% include "dashboard/announcement/new_announcement.html" %}
# {% else %}
#     {% include "dashboard/announcement/permission_denied.html" %}
# {% endif %}

# 仅供查阅

ANNOUNCEMENT_PUBLISH = '%publish_announcement%'  # 是否允许发布公告
POLICE_CASES_WATCH = '%police_cases_watch%'  # 是否允许查看报案列表
POLICE_CASES_ADD = '%police_cases_add%'  # 是否允许报案
DECLARATION_ANIMALS = '%declaration_animals%'  # 是否允许申报动物
DECLARATION_BUILDINGS = '%declaration_buildings%'  # 是否允许申报建筑物
DECLARATION_WATCH = '%declaration_watch%'  # 是否允许查看申报中心
