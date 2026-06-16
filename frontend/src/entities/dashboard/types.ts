export interface Dashboard {
  id: string;
  title: string;
  tiles: DashboardTile[];
  filters: CrossFilterBinding[];
  createdAt: string;
  updatedAt: string;
}

interface DashboardTile {
  id: string;
  questionId: string;
  position: TilePosition;
}

interface TilePosition {
  row: number;
  col: number;
  width: number;
  height: number;
}

interface CrossFilterBinding {
  sourceTileId: string;
  column: string;
  targetTileIds: string[];
}
