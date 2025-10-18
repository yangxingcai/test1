import pygame
import sys
import random
import time

# 初始化pygame
pygame.init()

# 游戏常量
CELL_SIZE = 30
GRID_X_OFFSET = 50
GRID_Y_OFFSET = 100

# 苹果设计规范颜色系统
# 背景色
BACKGROUND_PRIMARY = (242, 242, 247)  # iOS系统背景色
BACKGROUND_SECONDARY = (255, 255, 255)  # 卡片背景色
BACKGROUND_TERTIARY = (229, 229, 234)  # 分组背景色

# 文字颜色
LABEL_PRIMARY = (0, 0, 0)  # 主要文字
LABEL_SECONDARY = (60, 60, 67)  # 次要文字
LABEL_TERTIARY = (60, 60, 67, 0.6)  # 第三级文字

# 系统颜色
SYSTEM_BLUE = (0, 122, 255)
SYSTEM_GREEN = (52, 199, 89)
SYSTEM_ORANGE = (255, 149, 0)
SYSTEM_RED = (255, 59, 48)
SYSTEM_PURPLE = (175, 82, 222)
SYSTEM_YELLOW = (255, 204, 0)
SYSTEM_PINK = (255, 45, 85)
SYSTEM_GRAY = (142, 142, 147)

# 游戏颜色
CELL_COVERED = (200, 200, 200)  # 未点击的格子
CELL_UNCOVERED = (245, 245, 247)  # 已点击的格子
CELL_FLAGGED = SYSTEM_RED  # 标记的格子
MINE_COLOR = SYSTEM_RED  # 地雷
BORDER_COLOR = (198, 198, 200)
WHITE = (255, 255, 255)

# 数字颜色
NUMBER_COLORS = [
    (0, 0, 0),      # 0 - 黑色
    (0, 122, 255),  # 1 - 蓝色
    (52, 199, 89),  # 2 - 绿色
    (255, 59, 48),  # 3 - 红色
    (128, 0, 128),  # 4 - 紫色
    (255, 149, 0),  # 5 - 橙色
    (0, 200, 200),  # 6 - 青色
    (0, 0, 0),      # 7 - 黑色
    (128, 128, 128) # 8 - 灰色
]

# 难度设置
DIFFICULTIES = {
    'easy': {'rows': 9, 'cols': 9, 'mines': 10},
    'medium': {'rows': 16, 'cols': 16, 'mines': 40},
    'hard': {'rows': 16, 'cols': 30, 'mines': 99}
}

class MinesweeperGame:
    def __init__(self):
        # 窗口设置
        self.width = 1000
        self.height = 700
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("扫雷 - Minesweeper")
        self.clock = pygame.time.Clock()
        
        # 游戏状态
        self.difficulty = 'easy'
        self.rows = DIFFICULTIES[self.difficulty]['rows']
        self.cols = DIFFICULTIES[self.difficulty]['cols']
        self.mines = DIFFICULTIES[self.difficulty]['mines']
        
        # 游戏板
        self.board = []
        self.revealed = []
        self.flagged = []
        self.game_over = False
        self.game_won = False
        self.first_click = True
        self.start_time = 0
        self.elapsed_time = 0
        
        # 苹果设计规范字体系统
        try:
            self.title_font = pygame.font.Font(None, 48)
            self.headline_font = pygame.font.Font(None, 32)
            self.body_font = pygame.font.Font(None, 20)
            self.caption_font = pygame.font.Font(None, 16)
            self.number_font = pygame.font.Font(None, 24)
        except:
            self.title_font = pygame.font.Font(None, 36)
            self.headline_font = pygame.font.Font(None, 28)
            self.body_font = pygame.font.Font(None, 18)
            self.caption_font = pygame.font.Font(None, 14)
            self.number_font = pygame.font.Font(None, 20)
        
        self.init_game()
    
    def init_game(self):
        """初始化游戏"""
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.revealed = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.flagged = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.game_over = False
        self.game_won = False
        self.first_click = True
        self.start_time = 0
        self.elapsed_time = 0
    
    def set_difficulty(self, difficulty):
        """设置难度"""
        if difficulty in DIFFICULTIES:
            self.difficulty = difficulty
            self.rows = DIFFICULTIES[difficulty]['rows']
            self.cols = DIFFICULTIES[difficulty]['cols']
            self.mines = DIFFICULTIES[difficulty]['mines']
            self.init_game()
    
    def place_mines(self, first_row, first_col):
        """放置地雷（避开第一次点击的位置）"""
        mines_placed = 0
        while mines_placed < self.mines:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            
            # 避开第一次点击的位置和周围8个格子
            if (row == first_row and col == first_col) or \
               (abs(row - first_row) <= 1 and abs(col - first_col) <= 1):
                continue
            
            if self.board[row][col] != -1:  # -1 表示地雷
                self.board[row][col] = -1
                mines_placed += 1
        
        # 计算每个格子周围的地雷数量
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col] != -1:
                    count = 0
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = row + dr, col + dc
                            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                                if self.board[nr][nc] == -1:
                                    count += 1
                    self.board[row][col] = count
    
    def reveal_cell(self, row, col):
        """揭示格子"""
        if (row < 0 or row >= self.rows or col < 0 or col >= self.cols or 
            self.revealed[row][col] or self.flagged[row][col]):
            return
        
        if self.first_click:
            self.place_mines(row, col)
            self.first_click = False
            self.start_time = time.time()
        
        self.revealed[row][col] = True
        
        if self.board[row][col] == -1:  # 踩到地雷
            self.game_over = True
            self.reveal_all_mines()
        elif self.board[row][col] == 0:  # 空白格子，自动揭示周围
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    self.reveal_cell(row + dr, col + dc)
        
        self.check_win()
    
    def toggle_flag(self, row, col):
        """切换标记状态"""
        if (row < 0 or row >= self.rows or col < 0 or col >= self.cols or 
            self.revealed[row][col]):
            return
        
        self.flagged[row][col] = not self.flagged[row][col]
    
    def reveal_all_mines(self):
        """揭示所有地雷"""
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col] == -1:
                    self.revealed[row][col] = True
    
    def check_win(self):
        """检查是否获胜"""
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col] != -1 and not self.revealed[row][col]:
                    return
        self.game_won = True
    
    def get_flagged_count(self):
        """获取标记数量"""
        return sum(sum(row) for row in self.flagged)
    
    def get_revealed_count(self):
        """获取已揭示格子数量"""
        return sum(sum(row) for row in self.revealed)
    
    def draw_grid(self):
        """绘制游戏网格"""
        # 计算网格位置使其居中
        grid_pixel_width = self.cols * CELL_SIZE
        grid_pixel_height = self.rows * CELL_SIZE
        offset_x = (self.width - grid_pixel_width) // 2
        offset_y = GRID_Y_OFFSET
        
        # 绘制游戏区域背景
        game_area_rect = pygame.Rect(
            offset_x - 5,
            offset_y - 5,
            grid_pixel_width + 10,
            grid_pixel_height + 10
        )
        pygame.draw.rect(self.screen, BACKGROUND_SECONDARY, game_area_rect, border_radius=12)
        pygame.draw.rect(self.screen, BORDER_COLOR, game_area_rect, 2, border_radius=12)
        
        # 绘制每个格子
        for row in range(self.rows):
            for col in range(self.cols):
                rect = pygame.Rect(
                    offset_x + col * CELL_SIZE,
                    offset_y + row * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )
                
                # 绘制格子背景
                if self.revealed[row][col]:
                    pygame.draw.rect(self.screen, CELL_UNCOVERED, rect)
                elif self.flagged[row][col]:
                    pygame.draw.rect(self.screen, CELL_FLAGGED, rect)
                else:
                    pygame.draw.rect(self.screen, CELL_COVERED, rect)
                
                # 绘制格子内容
                if self.revealed[row][col]:
                    if self.board[row][col] == -1:  # 地雷
                        center = rect.center
                        pygame.draw.circle(self.screen, MINE_COLOR, center, CELL_SIZE // 3)
                        pygame.draw.circle(self.screen, WHITE, center, CELL_SIZE // 3, 2)
                    elif self.board[row][col] > 0:  # 数字
                        number_text = self.number_font.render(str(self.board[row][col]), True, 
                                                             NUMBER_COLORS[self.board[row][col]])
                        number_rect = number_text.get_rect(center=rect.center)
                        self.screen.blit(number_text, number_rect)
                elif self.flagged[row][col]:  # 标记
                    center = rect.center
                    pygame.draw.circle(self.screen, WHITE, center, CELL_SIZE // 4)
                    pygame.draw.circle(self.screen, MINE_COLOR, center, CELL_SIZE // 4, 3)
                
                # 绘制格子边框
                pygame.draw.rect(self.screen, BORDER_COLOR, rect, 1)
    
    def draw_header(self):
        """绘制顶部标题栏"""
        # 标题
        title_text = self.title_font.render("扫雷", True, LABEL_PRIMARY)
        title_rect = title_text.get_rect(center=(self.width // 2, 35))
        self.screen.blit(title_text, title_rect)
        
        # 难度选择按钮
        button_width = 80
        button_height = 30
        button_y = 60
        
        difficulties = ['easy', 'medium', 'hard']
        button_x = (self.width - len(difficulties) * (button_width + 10)) // 2
        
        for i, diff in enumerate(difficulties):
            btn_rect = pygame.Rect(button_x + i * (button_width + 10), button_y, button_width, button_height)
            
            # 按钮颜色
            if self.difficulty == diff:
                btn_color = SYSTEM_BLUE
                text_color = WHITE
            else:
                btn_color = BACKGROUND_TERTIARY
                text_color = LABEL_PRIMARY
            
            pygame.draw.rect(self.screen, btn_color, btn_rect, border_radius=8)
            pygame.draw.rect(self.screen, BORDER_COLOR, btn_rect, 1, border_radius=8)
            
            diff_text = self.caption_font.render(diff.title(), True, text_color)
            diff_rect = diff_text.get_rect(center=btn_rect.center)
            self.screen.blit(diff_text, diff_rect)
    
    def draw_info(self):
        """绘制游戏信息"""
        # 更新游戏时间
        if not self.first_click and not self.game_over and not self.game_won:
            self.elapsed_time = int(time.time() - self.start_time)
        
        # 信息卡片位置
        info_x = 50
        info_y = self.height - 150
        
        # 统计信息卡片
        stats_card = pygame.Rect(info_x - 10, info_y - 10, 200, 120)
        pygame.draw.rect(self.screen, BACKGROUND_SECONDARY, stats_card, border_radius=12)
        pygame.draw.rect(self.screen, BORDER_COLOR, stats_card, 1, border_radius=12)
        
        # 统计信息
        time_text = self.body_font.render(f"时间: {self.elapsed_time}s", True, LABEL_PRIMARY)
        mines_text = self.body_font.render(f"地雷: {self.mines - self.get_flagged_count()}", True, LABEL_PRIMARY)
        revealed_text = self.body_font.render(f"已揭示: {self.get_revealed_count()}", True, LABEL_PRIMARY)
        
        self.screen.blit(time_text, (info_x, info_y))
        self.screen.blit(mines_text, (info_x, info_y + 25))
        self.screen.blit(revealed_text, (info_x, info_y + 50))
        
        # 控制说明卡片
        controls_x = self.width - 250
        controls_y = self.height - 200
        controls_card = pygame.Rect(controls_x - 10, controls_y - 10, 240, 180)
        pygame.draw.rect(self.screen, BACKGROUND_SECONDARY, controls_card, border_radius=12)
        pygame.draw.rect(self.screen, BORDER_COLOR, controls_card, 1, border_radius=12)
        
        controls_title = self.headline_font.render("控制", True, LABEL_PRIMARY)
        title_rect = controls_title.get_rect(center=(controls_x + 110, controls_y + 10))
        self.screen.blit(controls_title, title_rect)
        
        controls = [
            ("左键", "点击揭示"),
            ("右键", "标记地雷"),
            ("R", "重新开始"),
            ("ESC", "退出")
        ]
        
        for i, (key, desc) in enumerate(controls):
            key_text = self.body_font.render(key, True, SYSTEM_BLUE)
            desc_text = self.caption_font.render(desc, True, LABEL_SECONDARY)
            self.screen.blit(key_text, (controls_x, controls_y + 35 + i * 25))
            self.screen.blit(desc_text, (controls_x, controls_y + 35 + i * 25 + 20))
    
    def draw_game_over(self):
        """绘制游戏结束界面"""
        # 苹果设计规范：绘制游戏结束模态框
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # 模态框
        modal_width = 400
        modal_height = 300
        modal_x = (self.width - modal_width) // 2
        modal_y = (self.height - modal_height) // 2
        
        modal_rect = pygame.Rect(modal_x, modal_y, modal_width, modal_height)
        pygame.draw.rect(self.screen, BACKGROUND_SECONDARY, modal_rect, border_radius=20)
        pygame.draw.rect(self.screen, BORDER_COLOR, modal_rect, 2, border_radius=20)
        
        if self.game_won:
            # 获胜界面
            result_text = self.title_font.render("恭喜获胜！", True, SYSTEM_GREEN)
            time_text = self.headline_font.render(f"用时: {self.elapsed_time}秒", True, LABEL_PRIMARY)
            restart_text = self.body_font.render("按 R 重新开始", True, LABEL_SECONDARY)
        else:
            # 失败界面
            result_text = self.title_font.render("游戏结束", True, SYSTEM_RED)
            time_text = self.headline_font.render(f"用时: {self.elapsed_time}秒", True, LABEL_PRIMARY)
            restart_text = self.body_font.render("按 R 重新开始", True, LABEL_SECONDARY)
        
        result_rect = result_text.get_rect(center=(modal_x + modal_width // 2, modal_y + 80))
        time_rect = time_text.get_rect(center=(modal_x + modal_width // 2, modal_y + 130))
        restart_rect = restart_text.get_rect(center=(modal_x + modal_width // 2, modal_y + 180))
        
        self.screen.blit(result_text, result_rect)
        self.screen.blit(time_text, time_rect)
        self.screen.blit(restart_text, restart_rect)
    
    def get_cell_from_pos(self, pos):
        """从鼠标位置获取格子坐标"""
        grid_pixel_width = self.cols * CELL_SIZE
        grid_pixel_height = self.rows * CELL_SIZE
        offset_x = (self.width - grid_pixel_width) // 2
        offset_y = GRID_Y_OFFSET
        
        x, y = pos
        col = (x - offset_x) // CELL_SIZE
        row = (y - offset_y) // CELL_SIZE
        
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return row, col
        return None
    
    def reset_game(self):
        """重置游戏"""
        self.init_game()
    
    def run(self):
        """运行游戏主循环"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # 左键
                        cell = self.get_cell_from_pos(event.pos)
                        if cell:
                            row, col = cell
                            self.reveal_cell(row, col)
                    
                    elif event.button == 3:  # 右键
                        cell = self.get_cell_from_pos(event.pos)
                        if cell:
                            row, col = cell
                            self.toggle_flag(row, col)
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # 左键释放
                        # 检查是否点击了难度按钮
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        if 60 <= mouse_y <= 90:  # 难度按钮区域
                            button_width = 80
                            button_height = 30
                            button_y = 60
                            difficulties = ['easy', 'medium', 'hard']
                            button_x = (self.width - len(difficulties) * (button_width + 10)) // 2
                            
                            for i, diff in enumerate(difficulties):
                                btn_rect = pygame.Rect(button_x + i * (button_width + 10), button_y, button_width, button_height)
                                if btn_rect.collidepoint(mouse_x, mouse_y):
                                    self.set_difficulty(diff)
                                    break
            
            # 绘制游戏
            self.screen.fill(BACKGROUND_PRIMARY)
            self.draw_header()
            self.draw_grid()
            self.draw_info()
            
            if self.game_over or self.game_won:
                self.draw_game_over()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = MinesweeperGame()
    game.run()
