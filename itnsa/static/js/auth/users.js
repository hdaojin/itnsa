new gridjs.Grid({
    columns: [
        { id: "id", name: "ID" },
        { id: "real_name", name: "姓名" },
        { id: "username", name: "用户名" },
        { id: "email", name: "邮箱" },
        { id: "role", name: "角色" },
        { id: "is_active", name: "是否激活" },
    ],
    data: [
        {% for user in users %}
        {
            id: "{{ user.id }}",
            real_name: "{{ user.real_name }}",
            username: "{{ user.username }}",
            email: "{{ user.email }}",
            role: "{{ user.role }}",
            is_active: "{{ user.is_active }}"
        },
        {% endfor %}
    ],
    search: true,
    sort: true,
    pagination: true,
    language: {
        search: {
            placeholder: "搜索...",
        },
        pagination: {
            previous: "上一页",
            next: "下一页",
            showing: "显示",
            results: () => "行",
        },
    },
}).render(document.getElementById("users-table"));