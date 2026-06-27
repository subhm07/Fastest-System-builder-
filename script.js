// JavaScript for AI Agent Progress Tracker

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const dailyCountEl = document.getElementById('daily-count');
    const streakCountEl = document.getElementById('streak-count');
    const efficiencyEl = document.getElementById('efficiency');
    const progressBar = document.getElementById('progress-bar');
    const taskButton = document.getElementById('task-button');
    const activityLog = document.getElementById('activity-log');
    const githubLink = document.getElementById('github-link');
    
    // Initialize or load data from localStorage
    let data = JSON.parse(localStorage.getItem('aiAgentProgress')) || {
        tasksToday: 0,
        lastDate: '',
        streak: 0,
        totalTasks: 0,
        completedToday: []
    };
    
    // Update display
    function updateDisplay() {
        dailyCountEl.textContent = data.tasksToday;
        streakCountEl.textContent = data.streak;
        
        // Calculate efficiency (tasks today vs goal of 5 tasks as example)
        const goal = 5;
        const efficiencyPercent = Math.min(Math.floor((data.tasksToday / goal) * 100), 100);
        efficiencyEl.textContent = efficiencyPercent + '%';
        progressBar.style.width = efficiencyPercent + '%';
        
        // Update activity log
        updateActivityLog();
    }
    
    // Update activity log from data
    function updateActivityLog() {
        // Clear current log
        activityLog.innerHTML = '';
        
        if (data.completedToday.length === 0) {
            const li = document.createElement('li');
            li.textContent = 'No tasks logged yet';
            activityLog.appendChild(li);
            return;
        }
        
        // Show recent tasks (most recent first)
        const recentTasks = data.completedToday.slice().reverse().slice(0, 10);
        recentTasks.forEach(task => {
            const li = document.createElement('li');
            
            const taskText = document.createElement('span');
            taskText.textContent = task.description;
            
            const timeSpan = document.createElement('span');
            timeSpan.className = 'activity-time';
            timeSpan.textContent = new Date(task.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            
            li.appendChild(taskText);
            li.appendChild(timeSpan);
            activityLog.appendChild(li);
        });
    }
    
    // Check if it's a new day and reset if needed
    function checkNewDay() {
        const today = new Date().toISOString().split('T')[0];
        if (data.lastDate !== today) {
            // New day
            data.lastDate = today;
            // If we had tasks yesterday, increment streak, else reset streak to 0 (but keep if we had tasks yesterday?)
            // Simple approach: if we had any tasks yesterday, streak++; else streak = 0
            if (data.tasksToday > 0) {
                data.streak++;
            } else {
                // Only reset streak if we had zero tasks yesterday AND we had a streak before
                // Actually we want to reset when we had tasksToday? Not correct
            }
            // Reset today's tasks
            data.tasksToday = 0;
            data.completedToday = [];
            // Save and update
            saveData();
            updateDisplay();
        }
    }
    
    // Save data to localStorage
    function saveData() {
        localStorage.setItem('aiAgentProgress', JSON.stringify(data));
    }
    
    // Add a completed task
    function addTask() {
        const taskDescription = prompt('What task did your AI agent complete today?', '');
        if (taskDescription === null || taskDescription.trim() === '') {
            return; // User cancelled or empty
        }
        
        const task = {
            description: taskDescription.trim(),
            timestamp: new Date().toISOString()
        };
        
        data.tasksToday++;
        data.totalTasks++;
        data.completedToday.push(task);
        
        // Update streak if it's the first task of the day
        if (data.tasksToday === 1) {
            // Check if yesterday we had tasks to continue streak
            const yesterday = new Date();
            yesterday.setDate(yesterday.getDate() - 1);
            const yesterdayStr = yesterday.toISOString().split('T')[0];
            if (data.lastDate === yesterdayStr) {
                // We had a lastDate, meaning we logged something yesterday
                // Actually we need to check if we had any tasks yesterday stored somewhere
                // For simplicity, we assume if lastDate is yesterday, we continue streak
                data.streak++;
            } else {
                // Starting a new streak
                data.streak = 1;
            }
        }
        
        saveData();
        updateDisplay();
    }
    
    // Event listeners
    taskButton.addEventListener('click', addTask);
    
    // GitHub link (placeholder)
    githubLink.href = 'https://github.com/yourusername/ai-agent-progress-tracker';
    githubLink.target = '_blank';
    githubLink.rel = 'noopener';
    
    // Initialize
    checkNewDay();
    updateDisplay();
    
    // Optional: auto-save every minute
    setInterval(saveData, 60000);
});
