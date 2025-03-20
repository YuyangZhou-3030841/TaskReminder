// Flatpickr Initialisation and Calendar Event Handling
document.addEventListener("DOMContentLoaded", function() {

    const quickAddForm = document.getElementById('quickAddForm');
    if (quickAddForm) {
        quickAddForm.addEventListener('submit', function(e) {
            e.preventDefault();  // Blocking default form submission
            const form = this;
            const formData = new FormData(form);
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // After successful addition, the page is refreshed by constructing a new URL parameter based on the deadline date returned.
                    const newDeadline = data.task_deadline;  
                    const deadlineDateStr = newDeadline.split(' ')[0];
                    const now = new Date();
                    const year = now.getFullYear();
                    const month = (now.getMonth() + 1).toString().padStart(2, '0');
                    const day = now.getDate().toString().padStart(2, '0');
                    const todayStr = `${year}-${month}-${day}`;
                    const url = new URL(window.location.href);
                    url.searchParams.set('start_date', todayStr);
                    url.searchParams.set('end_date', deadlineDateStr);
                    window.location.href = url.pathname + "?" + url.searchParams.toString();
                } else {
                    console.error('Quick Add Task Error', data.errors);
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }

    // ----- Detailed Add Form -----
    const detailedAddForm = document.getElementById('detailedAddForm');
    if (detailedAddForm) {
        detailedAddForm.addEventListener('submit', function(e) {
            e.preventDefault();  // Blocking default form submission
            const form = this;
            const formData = new FormData(form);
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const newDeadline = data.task_deadline;
                    const deadlineDateStr = newDeadline.split(' ')[0];
                    const now = new Date();
                    const year = now.getFullYear();
                    const month = (now.getMonth() + 1).toString().padStart(2, '0');
                    const day = now.getDate().toString().padStart(2, '0');
                    const todayStr = `${year}-${month}-${day}`;
                    const url = new URL(window.location.href);
                    url.searchParams.set('start_date', todayStr);
                    url.searchParams.set('end_date', deadlineDateStr);
                    window.location.href = url.pathname + "?" + url.searchParams.toString();
                } else {
                    console.error('Detailed Add Task Error', data.errors);
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }

    const calendarInput = document.getElementById("calendarTrigger");
    const params = new URLSearchParams(window.location.search);
    // If end_date is not specified in the URL, it is set to the current date + 7 days by default.
    if (!params.has("end_date") && !calendarInput.value) {
        let today = new Date();
        today.setDate(today.getDate() + 7);
        calendarInput.value = today.toISOString().split('T')[0];
    }
    flatpickr("#calendarTrigger", {
        locale: "en",
        dateFormat: "Y-m-d",
        defaultDate: calendarInput.value,
        onChange: function(selectedDates, dateStr) {
            onCalendarChange(dateStr);
        }
    });
    if (params.has("end_date")) {
        calendarInput.value = params.get("end_date");
    }

    // Deadline for initialising Quick Add (to the minute)
    const quickDueDateInput = document.querySelector("#quickAddModal input[name='due_date']");
    if (quickDueDateInput) {
        flatpickr(quickDueDateInput, {
            enableTime: true,
            dateFormat: "Y-m-d H:i",
            locale: "en"
        });
    }
    // Initialise the deadline and start date for Detailed Add.
    const detailedDueDateInput = document.querySelector("#detailedAddModal input[name='due_date']");
    if (detailedDueDateInput) {
        flatpickr(detailedDueDateInput, {
            enableTime: true,
            dateFormat: "Y-m-d H:i",
            locale: "en"
        });
    }
    const detailedStartDateInput = document.querySelector("#detailedAddModal input[name='start_date']");
    if (detailedStartDateInput) {
        flatpickr(detailedStartDateInput, {
            enableTime: true,
            dateFormat: "Y-m-d H:i",
            locale: "en"
        });
    }
});

// Refresh the page according to the selected date URL parameter
function onCalendarChange(value) {
    const url = new URL(window.location.href);
    let now = new Date();
    let year = now.getFullYear();
    let month = (now.getMonth() + 1).toString().padStart(2, '0');
    let day = now.getDate().toString().padStart(2, '0');
    url.searchParams.set('start_date', `${year}-${month}-${day}`);
    url.searchParams.set('end_date', value);
    window.location.href = url.pathname + "?" + url.searchParams.toString();
}

// Search assignments
function searchTask() {
    const query = document.getElementById('taskSearchInput').value;
    if(query.trim() === ""){
        return;
    }
    const url = new URL(window.location.href);
    url.searchParams.delete('task_id');
    url.searchParams.set('search', query);
    window.location.href = url.pathname + "?" + url.searchParams.toString();
}

// Clear search criteria
function clearSearch() {
    document.getElementById('taskSearchInput').value = '';
    const url = new URL(window.location.href);
    url.searchParams.delete('search');
    url.searchParams.delete('task_id');
    window.location.href = url.pathname + "?" + url.searchParams.toString();
}

// Deleting tasks (calling back-end views via AJAX)
function deleteTask(deleteUrl) {
    if (confirm('Sure you want to delete this task?')) {
        fetch(deleteUrl, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const url = new URL(window.location.href);
                url.searchParams.delete('task_id');
                window.location.href = url.pathname + "?" + url.searchParams.toString();
            } else {
                alert('Failed to delete task');
            }
        })
        .catch(error => {
            console.error('Delete task error:', error);
            alert('Error deleting task');
        });
    }
}

// Clock update and time zone setting
function onTimezoneChange(tz) {
    document.cookie = "user_timezone=" + tz + ";path=/;max-age=31536000";
    updateClock();
}

function updateClock() {
    const userTimeZone = getCookie("user_timezone") || "Asia/Shanghai";
    const now = new Date();
    const options = { hour: '2-digit', minute: '2-digit', second: '2-digit', timeZone: userTimeZone };
    const formatter = new Intl.DateTimeFormat([], options);
    document.getElementById("currentTimeDisplay").textContent = formatter.format(now);
}

setInterval(updateClock, 1000);
updateClock();

// Clear selected tasks when clicking on a blank area of the page 
document.addEventListener('click', function(e) {
    if (e.target.closest('.task-detail') || e.target.closest('.sidebar') || e.target.closest('.modal')) {
        return;
    }
    const url = new URL(window.location.href);
    if (url.searchParams.has('task_id')) {
        url.searchParams.delete('task_id');
        window.location.href = url.pathname + "?" + url.searchParams.toString();
    }
});

// Widget toggle button event (opens widget mode window)
document.getElementById('widgetToggle')?.addEventListener('click', function() {
    window.open(window.location.pathname + "?widget_mode=1", "widgetWindow", "width=300,height=400,top=100,left=100,toolbar=no,scrollbars=no,resizable=yes");
});
