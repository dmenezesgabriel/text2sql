export interface Dashboard {
  id: string;
  title: string;
  tiles: DashboardTile[];
  createdAt: string;
  updatedAt: string;
}

export interface DashboardTile {
  id: string;
  questionId: string;
  position: TilePosition;
}

export interface TilePosition {
  row: number;
  col: number;
  width: number;
  height: number;
}

export interface CrossFilterBinding {
  sourceTileId: string;
  column: string;
  targetTileIds: string[];
}
