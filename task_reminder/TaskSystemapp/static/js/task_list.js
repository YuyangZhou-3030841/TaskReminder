// 在原有任务列表初始化后添加
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

// 数据更新时
vs.updateData(allTasks);