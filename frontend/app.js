document.addEventListener('DOMContentLoaded', () => {
    const tg = window.Telegram.WebApp;
    tg.ready();
    tg.expand(); // Make the web app full height

    const gameList = document.getElementById('game-list');
    const refreshBtn = document.getElementById('refresh-btn');

    function fetchGames() {
        gameList.innerHTML = '<p>Loading open games...</p>';
        fetch('/api/games')
            .then(response => response.json())
            .then(data => {
                gameList.innerHTML = ''; // Clear loading text
                if (data.games && data.games.length > 0) {
                    data.games.forEach(game => {
                        const card = document.createElement('div');
                        card.className = 'game-card';
                        card.innerHTML = `
                            <div class="card-top">
                                <div class="player-info">
                                    <img src="${game.creator_avatar}" alt="Avatar">
                                    <div>
                                        <div class="player-name">${game.creator_name}</div>
                                        <div class="game-mode">👑 1 Token Home</div>
                                    </div>
                                </div>
                                <div class="game-stats">
                                    <span>Stake</span>
                                    <span>${game.stake} ETB</span>
                                </div>
                                <div class="game-stats">
                                    <span>Prize</span>
                                    <span class="prize">${game.prize} ETB</span>
                                </div>
                            </div>
                            <div class="card-bottom">
                                <button class="join-btn" data-game-id="${game.id}">Join</button>
                            </div>
                        `;
                        gameList.appendChild(card);
                    });
                } else {
                    gameList.innerHTML = '<p>No open games found. Create one!</p>';
                }
            })
            .catch(error => {
                console.error('Error fetching games:', error);
                gameList.innerHTML = '<p>Could not load games. Please try again.</p>';
            });
    }

    // Handle clicks on "Join" buttons
    gameList.addEventListener('click', event => {
        if (event.target.classList.contains('join-btn')) {
            const gameId = event.target.getAttribute('data-game-id');
            // This sends a message back to your bot with the game ID
            tg.sendData(`join_game_${gameId}`);
            tg.close(); // Close the web app after clicking
        }
    });
    
    refreshBtn.addEventListener('click', fetchGames);

    // Initial load of games
    fetchGames();
});