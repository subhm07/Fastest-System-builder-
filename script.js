// JavaScript for the AI Agent Dashboard
document.addEventListener('DOMContentLoaded', function() {
    const taskInput = document.getElementById('task-input');
    const addTaskBtn = document.getElementById('add-task');
    const taskList = document.getElementById('task-list');
    const tasksCompletedEl = document.getElementById('tasks-completed');
    const focusTimeEl = document.getElementById('focus-time');
    const successRateEl = document.getElementById('success-rate');

    // Load tasks from localStorage or initialize
    let tasks = JSON.parse(localStorage.getItem('aiAgentTasks')) || [];
    let focusTime = parseInt(localStorage.getItem('aiAgentFocusTime')) || 0;
    let completedTasks = parseInt(localStorage.getItem('aiAgentCompletedTasks')) || 0;

    // Update the display
    function updateDisplay() {
        tasksCompletedEl.textContent = completedTasks;
        focusTimeEl.textContent = focusTime + ' min';
        const successRate = tasks.length > 0 ? Math.round((completedTasks / tasks.length) * 100) : 0;
        successRateEl.textContent = successRate + '%';

        // Render task list
        taskList.innerHTML = '';
        tasks.forEach((task, index) => {
            const li = document.createElement('li');
            li.innerHTML = `
                <span>${task.text}</span>
                <button onclick="toggleTask(${index})">${task.completed ? 'Undo' : 'Complete'}</button>
                <button onclick="deleteTask(${index})">Delete</button>
            `;
            if (task.completed) {
                li.classList.add('completed');
            }
            taskList.appendChild(li);
        });
    }

    // Add a new task
    window.addTask = function() {
        const text = taskInput.value.trim();
        if (text) {
            tasks.push({ text: text, completed: false });
            taskInput.value = '';
            saveAndUpdate();
        }
    };

    // Toggle task completion
    window.toggleTask = function(index) {
        tasks[index].completed = !tasks[index].completed;
        if (tasks[index].completed) {
            completedTasks++;
        } else {
            completedTasks--;
        }
        saveAndUpdate();
    };

    // Delete a task
    window.deleteTask = function(index) {
        if (tasks[index].completed) {
            completedTasks--;
        }
        tasks.splice(index, 1);
        saveAndUpdate();
    };

    // Save to localStorage and update display
    function saveAndUpdate() {
        localStorage.setItem('aiAgentTasks', JSON.stringify(tasks));
        localStorage.setItem('aiAgentCompletedTasks', completedTasks);
        updateDisplay();
    }

    // Event listeners
    addTaskBtn.addEventListener('click', addTask);
    taskInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            addTask();
        }
    });

    // Initial display update
    updateDisplay();
});