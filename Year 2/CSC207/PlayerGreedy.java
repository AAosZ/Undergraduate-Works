package ca.utoronto.utm.assignment1.othello;

public class PlayerGreedy {

	private OthelloBoard board;
	private char player;

	public PlayerGreedy(OthelloBoard board, char player) {
        this.board = board;
		this.player = player;
	}

	private int flipCount(int row, int col, int drow, int dcol) {
		if (board.alternation(row += drow, col += dcol, drow, dcol) == player) {
			int count = 0;

			while (board.validCoordinate(row, col)) {
				if (board.get(row, col) == player) {
					return count;
				}
				if (board.get(row, col) != board.EMPTY && board.get(row, col) != player) {
					count++;
				}
				else {
					return 0;
				}
				row += drow;
				col += dcol;
			}
		}
		return 0;
	}

	public Move getMove() {
		int maxFlips = 0;
		int[] bestMove = {0, 0};
		Move bestMove1 = null;

		int[] drow = {0, 1, 0, -1, 1, -1, 1, -1};
		int[] dcol = {1, 0, -1, 0, 1, -1, -1, 1};

		for (int row = 0; row < board.getDimension(); row++) {
			for (int col = 0; col < board.getDimension(); col++) {
				if (board.get(row, col) == board.EMPTY) {
					int total = 0;

					for (int i = 0; i < drow.length; i++) {
						total += flipCount(row, col, drow[i], dcol[i]);
					}
					if (total > maxFlips) {
						maxFlips = total;
						bestMove = new int[]{row, col};
					}
				}
			}
		}
		bestMove1 = new Move(bestMove[0], bestMove[1]);
        return bestMove1;
	}
}
