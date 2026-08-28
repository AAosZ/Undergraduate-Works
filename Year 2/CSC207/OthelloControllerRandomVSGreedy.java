package ca.utoronto.utm.assignment1.othello;

public class OthelloControllerRandomVSGreedy {

	protected Othello othello;
	protected OthelloBoard board;
	PlayerRandom player1;
	PlayerGreedy player2;
	int p1wins = 0;
	int p2wins = 0;

	public OthelloControllerRandomVSGreedy() {
		this.othello = new Othello();
		this.board = othello.getGame();
		this.player1 = new PlayerRandom(this.board, OthelloBoard.P1);
		this.player2 = new PlayerGreedy(this.board, OthelloBoard.P2);
	}

	public int[] play(int numGames) {
		int games = 0;
		while (games < numGames) {
			this.othello = new Othello();
			this.board = othello.getGame();
			this.player1 = new PlayerRandom(this.board, OthelloBoard.P1);
			this.player2 = new PlayerGreedy(this.board, OthelloBoard.P2);

			while (!othello.isGameOver()) {

				Move move = null;
				char whosTurn = othello.getWhosTurn();

				if (whosTurn == OthelloBoard.P1)
					move = player1.getMove();
				if (whosTurn == OthelloBoard.P2)
					move = player2.getMove();

				othello.move(move.getRow(), move.getCol());
			}
			char winner = othello.getWinner();
			if (winner == OthelloBoard.P1) {
				p1wins++;
			}
			else if (winner == OthelloBoard.P2) {
				p2wins++;
			}
			games += 1;
		}
		return new int[]{p1wins, p2wins};
	}

	public static void main(String[] args) {

		int p1wins = 0, p2wins = 0, numGames = 10000;
		OthelloControllerRandomVSGreedy oc = new OthelloControllerRandomVSGreedy();
		int[] results = oc.play(numGames);
		p1wins += results[0];
		p2wins += results[1];
		System.out.println("Probability P1 wins=" + (float) p1wins / numGames);
		System.out.println("Probability P2 wins=" + (float) p2wins / numGames);
	}
}
