// 修改FullCalendar初始化配置
const calendar = new FullCalendar.Calendar(calendarEl, {
    events: function(fetchInfo, successCallback) {
        fetch(`/api/tasks/?start=${fetchInfo.startStr}&end=${fetchInfo.endStr}`)
            .then(res => res.json())
            .then(successCallback);
    }
});