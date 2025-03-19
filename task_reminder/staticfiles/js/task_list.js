// Added after the initialisation of the original task list
import { VirtualScroll } from 'virtual-scroll';

const vs = new VirtualScroll({
    container: document.querySelector('.task-list'),
    itemHeight: 60,
    renderItem: (task) => {
        const div = document.createElement('div');
        div.className = 'task-item';
        div.innerHTML = `
            <input type="checkbox" data-task-id="${task.id}">
            <span>${task.title}</span>
        `;
        return div;
    }
});

// When updating data
vs.updateData(allTasks);