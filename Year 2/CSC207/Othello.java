package ca.utoronto.utm.assignment1.othello;

import java.util.Random;

public class Othello {

	public static final int DIMENSION = 8;
	private char whosTurn = OthelloBoard.P1;
	private final int numMoves = 0;

	public OthelloBoard game = new OthelloBoard(DIMENSION);
	public char getWhosTurn() {
		if (game.hasMove() == OthelloBoard.BOTH) {
			return whosTurn;
		}
		else if (game.hasMove() == OthelloBoard.P1) {
			return OthelloBoard.P1;
		}
		else if (game.hasMove() == OthelloBoard.P2) {
			return OthelloBoard.P2;
		}
		else {
			return OthelloBoard.EMPTY;
        }
    }
	public boolean move(int row, int col) {
        char currentP = this.getWhosTurn();

		if (game.move(row, col, currentP)) {
			if (currentP == OthelloBoard.P1) {
				whosTurn = OthelloBoard.P2;
				return true;
			}
			if (currentP == OthelloBoard.P2) {
				whosTurn = OthelloBoard.P1;
				return true;
			}
		}
		return false;
    }

	public int getCount(char player) {
		return game.getCount(player);
	}

	public char getWinner() {
		if (game.hasMove() == OthelloBoard.BOTH || game.hasMove() == OthelloBoard.P1 || game.hasMove() == OthelloBoard.P2) {
			return OthelloBoard.EMPTY;
		}

		if (game.getCount(OthelloBoard.P1) > game.getCount(OthelloBoard.P2)) {
			return OthelloBoard.P1;
		}
		else if (game.getCount(OthelloBoard.P2) > game.getCount(OthelloBoard.P1)) {
			return OthelloBoard.P2;
		}
		else {
			return OthelloBoard.EMPTY;
		}
	}

	public boolean isGameOver() {
		return game.hasMove() == OthelloBoard.EMPTY;
	}
	public OthelloBoard getGame() {
		return this.game;
    }

	public String getBoardString() {
		return "";
	}

	public static void main(String[] args) {
		
		Random rand = new Random();

		Othello o = new Othello();
		System.out.println(o.getBoardString());
		while (!o.isGameOver()) {
			int row = rand.nextInt(8);
			int col = rand.nextInt(8);

			if (o.move(row, col)) {
				System.out.println("makes move (" + row + "," + col + ")");
				System.out.println(o.getBoardString() + o.getWhosTurn() + " moves next");
			}
		}

	}
}