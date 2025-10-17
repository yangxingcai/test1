import pygame
import random
import sys

# 初始化pygame
pygame.init()

# 游戏常量
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 30
GRID_X_OFFSET = 50
GRID_Y_OFFSET = 50

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

# 俄罗斯方块颜色（使用苹果系统色）
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = SYSTEM_BLUE
BLUE = (0, 48, 255)  # 深蓝色
ORANGE = SYSTEM_ORANGE
YELLOW = SYSTEM_YELLOW
GREEN = SYSTEM_GREEN
PURPLE = SYSTEM_PURPLE
RED = SYSTEM_RED
GRAY = (142, 142, 147)  # 苹果灰色

# 边框和分割线
SEPARATOR = (198, 198, 200)
FILL = (120, 120, 128, 0.2)

# 俄罗斯方块形状定义
SHAPES = [
    # I形状
    [['.....',
      '..#..',
      '..#..',
      '..#..',
      '..#..'],
     ['.....',
      '.....',
      '####.',
      '.....',
      '.....']],
    
    # O形状
    [['.....',
      '.....',
      '.##..',
      '.##..',
      '.....']],
    
    # T形状
    [['.....',
      '.....',
      '.#...',
      '###..',
      '.....'],
     ['.....',
      '.....',
      '.#...',
      '.##..',
      '.#...'],
     ['.....',
      '.....',
      '.....',
      '###..',
      '.#...'],
     ['.....',
      '.....',
      '.#...',
      '##...',
      '.#...']],
    
    # S形状
    [['.....',
      '.....',
      '.##..',
      '##...',
      '.....'],
     ['.....',
      '.#...',
      '.##..',
      '..#..',
      '.....']],
    
    # Z形状
    [['.....',
      '.....',
      '##...',
      '.##..',
      '.....'],
     ['.....',
      '..#..',
      '.##..',
      '.#...',
      '.....']],
    
    # J形状
    [['.....',
      '.#...',
      '.#...',
      '##...',
      '.....'],
     ['.....',
      '.....',
      '#....',
      '###..',
      '.....'],
     ['.....',
      '.##..',
      '.#...',
      '.#...',
      '.....'],
     ['.....',
      '.....',
      '###..',
      '..#..',
      '.....']],
    
    # L形状
    [['.....',
      '..#..',
      '..#..',
      '.##..',
      '.....'],
     ['.....',
      '.....',
      '###..',
      '#....',
      '.....'],
     ['.....',
      '##...',
      '.#...',
      '.#...',
      '.....'],
     ['.....',
      '.....',
      '..#..',
      '###..',
      '.....']]
]

SHAPE_COLORS = [CYAN, YELLOW, PURPLE, GREEN, RED, BLUE, ORANGE]

class TetrisPiece:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.shape = random.randint(0, len(SHAPES) - 1)
        self.rotation = 0
        self.color = SHAPE_COLORS[self.shape]
    
    def get_rotated_shape(self):
        return SHAPES[self.shape][self.rotation % len(SHAPES[self.shape])]
    
    def get_cells(self):
        cells = []
        shape = self.get_rotated_shape()
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell == '#':
                    cells.append((self.x + j, self.y + i))
        return cells

class TetrisGame:
    def __init__(self):
        # 苹果设计规范：更大的窗口，更好的比例
        self.width = 800
        self.height = 700
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("俄罗斯方块")
        self.clock = pygame.time.Clock()
        
        # 游戏状态
        self.grid = [[BACKGROUND_SECONDARY for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.get_new_piece()
        self.next_piece = self.get_new_piece()
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_time = 0
        self.fall_speed = 500  # 毫秒
        self.paused = False
        
        # 苹果设计规范字体系统
        try:
            # 尝试使用系统字体（苹果风格）
            self.title_font = pygame.font.Font(None, 48)  # 大标题
            self.headline_font = pygame.font.Font(None, 32)  # 标题
            self.body_font = pygame.font.Font(None, 20)  # 正文
            self.caption_font = pygame.font.Font(None, 16)  # 说明文字
        except:
            # 备用字体
            self.title_font = pygame.font.Font(None, 36)
            self.headline_font = pygame.font.Font(None, 28)
            self.body_font = pygame.font.Font(None, 18)
            self.caption_font = pygame.font.Font(None, 14)
    
    def get_new_piece(self):
        return TetrisPiece(GRID_WIDTH // 2 - 2, 0)
    
    def is_valid_position(self, piece, dx=0, dy=0, rotation=None):
        if rotation is None:
            rotation = piece.rotation
        
        # 临时保存当前状态
        old_x, old_y, old_rotation = piece.x, piece.y, piece.rotation
        piece.x += dx
        piece.y += dy
        piece.rotation = rotation
        
        cells = piece.get_cells()
        valid = True
        
        for x, y in cells:
            if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
                valid = False
                break
            if y >= 0 and self.grid[y][x] != BLACK:
                valid = False
                break
        
        # 恢复状态
        piece.x, piece.y, piece.rotation = old_x, old_y, old_rotation
        return valid
    
    def place_piece(self, piece):
        cells = piece.get_cells()
        for x, y in cells:
            if y >= 0:
                self.grid[y][x] = piece.color
        
        # 检查并清除完整的行
        self.clear_lines()
        
        # 生成新方块
        self.current_piece = self.next_piece
        self.next_piece = self.get_new_piece()
        
        # 检查游戏结束
        if not self.is_valid_position(self.current_piece):
            return False
        return True
    
    def clear_lines(self):
        lines_to_clear = []
        for y in range(GRID_HEIGHT):
            if all(cell != BLACK for cell in self.grid[y]):
                lines_to_clear.append(y)
        
        # 清除行
        for y in lines_to_clear:
            del self.grid[y]
            self.grid.insert(0, [BLACK for _ in range(GRID_WIDTH)])
        
        # 更新分数和等级
        if lines_to_clear:
            self.lines_cleared += len(lines_to_clear)
            self.score += len(lines_to_clear) * 100 * self.level
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = max(50, 500 - (self.level - 1) * 50)
    
    def move_piece(self, dx, dy):
        if self.is_valid_position(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            return True
        return False
    
    def rotate_piece(self):
        new_rotation = (self.current_piece.rotation + 1) % len(SHAPES[self.current_piece.shape])
        if self.is_valid_position(self.current_piece, rotation=new_rotation):
            self.current_piece.rotation = new_rotation
            return True
        return False
    
    def drop_piece(self):
        if not self.move_piece(0, 1):
            return self.place_piece(self.current_piece)
        return True
    
    def hard_drop(self):
        while self.move_piece(0, 1):
            pass
        return self.place_piece(self.current_piece)
    
    def draw_grid(self):
        # 苹果设计规范：绘制游戏区域背景
        game_area_rect = pygame.Rect(
            GRID_X_OFFSET - 5,
            GRID_Y_OFFSET - 5,
            GRID_WIDTH * CELL_SIZE + 10,
            GRID_HEIGHT * CELL_SIZE + 10
        )
        pygame.draw.rect(self.screen, BACKGROUND_SECONDARY, game_area_rect, border_radius=12)
        pygame.draw.rect(self.screen, SEPARATOR, game_area_rect, 2, border_radius=12)
        
        # 绘制网格
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(
                    GRID_X_OFFSET + x * CELL_SIZE,
                    GRID_Y_OFFSET + y * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )
                # 苹果设计规范：使用圆角矩形
                pygame.draw.rect(self.screen, self.grid[y][x], rect, border_radius=4)
                pygame.draw.rect(self.screen, SEPARATOR, rect, 1, border_radius=4)
    
    def draw_piece(self, piece, offset_x=0, offset_y=0):
        cells = piece.get_cells()
        for x, y in cells:
            if 0 <= x < GRID_WIDTH and y >= 0:
                rect = pygame.Rect(
                    GRID_X_OFFSET + (x + offset_x) * CELL_SIZE,
                    GRID_Y_OFFSET + (y + offset_y) * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )
                # 苹果设计规范：使用圆角矩形和阴影效果
                pygame.draw.rect(self.screen, piece.color, rect, border_radius=4)
                pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=4)
    
    def draw_next_piece(self):
        # 苹果设计规范：绘制下一个方块预览卡片
        next_x = GRID_X_OFFSET + GRID_WIDTH * CELL_SIZE + 30
        next_y = GRID_Y_OFFSET + 50
        
        # 绘制卡片背景
        card_rect = pygame.Rect(next_x - 10, next_y - 40, 160, 120)
        pygame.draw.rect(self.screen, BACKGROUND_SECONDARY, card_rect, border_radius=12)
        pygame.draw.rect(self.screen, SEPARATOR, card_rect, 1, border_radius=12)
        
        # 绘制标题
        text = self.headline_font.render("下一个", True, LABEL_PRIMARY)
        text_rect = text.get_rect(center=(next_x + 70, next_y - 20))
        self.screen.blit(text, text_rect)
        
        # 绘制下一个方块
        cells = self.next_piece.get_cells()
        if cells:
            min_x = min(x for x, y in cells)
            min_y = min(y for x, y in cells)
            
            for x, y in cells:
                rect = pygame.Rect(
                    next_x + (x - min_x) * 20,
                    next_y + (y - min_y) * 20,
                    20,
                    20
                )
                pygame.draw.rect(self.screen, self.next_piece.color, rect, border_radius=3)
                pygame.draw.rect(self.screen, WHITE, rect, 1, border_radius=3)
    
    def draw_info(self):
        # 苹果设计规范：绘制信息卡片
        info_x = GRID_X_OFFSET + GRID_WIDTH * CELL_SIZE + 30
        info_y = GRID_Y_OFFSET + 200
        
        # 分数卡片
        score_card = pygame.Rect(info_x - 10, info_y - 10, 160, 100)
        pygame.draw.rect(self.screen, BACKGROUND_SECONDARY, score_card, border_radius=12)
        pygame.draw.rect(self.screen, SEPARATOR, score_card, 1, border_radius=12)
        
        # 分数信息
        score_text = self.headline_font.render(f"{self.score:,}", True, SYSTEM_BLUE)
        score_label = self.caption_font.render("分数", True, LABEL_SECONDARY)
        level_text = self.body_font.render(f"等级 {self.level}", True, LABEL_PRIMARY)
        lines_text = self.body_font.render(f"消除 {self.lines_cleared} 行", True, LABEL_PRIMARY)
        
        self.screen.blit(score_label, (info_x, info_y))
        score_rect = score_text.get_rect(center=(info_x + 70, info_y + 25))
        self.screen.blit(score_text, score_rect)
        self.screen.blit(level_text, (info_x, info_y + 45))
        self.screen.blit(lines_text, (info_x, info_y + 65))
        
        # 控制说明卡片
        controls_y = info_y + 120
        controls_card = pygame.Rect(info_x - 10, controls_y - 10, 160, 180)
        pygame.draw.rect(self.screen, BACKGROUND_SECONDARY, controls_card, border_radius=12)
        pygame.draw.rect(self.screen, SEPARATOR, controls_card, 1, border_radius=12)
        
        controls_title = self.headline_font.render("控制", True, LABEL_PRIMARY)
        title_rect = controls_title.get_rect(center=(info_x + 70, controls_y + 10))
        self.screen.blit(controls_title, title_rect)
        
        controls = [
            ("← →", "移动"),
            ("↓", "软降"),
            ("↑", "旋转"),
            ("空格", "硬降"),
            ("P", "暂停"),
            ("ESC", "退出")
        ]
        
        for i, (key, desc) in enumerate(controls):
            key_text = self.body_font.render(key, True, SYSTEM_BLUE)
            desc_text = self.caption_font.render(desc, True, LABEL_SECONDARY)
            self.screen.blit(key_text, (info_x, controls_y + 35 + i * 20))
            self.screen.blit(desc_text, (info_x + 50, controls_y + 35 + i * 20))
    
    def draw_game_over(self):
        # 苹果设计规范：绘制游戏结束模态框
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # 模态框
        modal_width = 400
        modal_height = 300
        modal_x = (self.width - modal_width) // 2
        modal_y = (self.height - modal_height) // 2
        
        modal_rect = pygame.Rect(modal_x, modal_y, modal_width, modal_height)
        pygame.draw.rect(self.screen, BACKGROUND_SECONDARY, modal_rect, border_radius=20)
        pygame.draw.rect(self.screen, SEPARATOR, modal_rect, 2, border_radius=20)
        
        # 游戏结束文本
        game_over_text = self.title_font.render("游戏结束", True, LABEL_PRIMARY)
        score_text = self.headline_font.render(f"最终分数: {self.score:,}", True, SYSTEM_BLUE)
        restart_text = self.body_font.render("按 R 重新开始", True, LABEL_SECONDARY)
        exit_text = self.body_font.render("按 ESC 退出", True, LABEL_SECONDARY)
        
        game_over_rect = game_over_text.get_rect(center=(modal_x + modal_width // 2, modal_y + 80))
        score_rect = score_text.get_rect(center=(modal_x + modal_width // 2, modal_y + 130))
        restart_rect = restart_text.get_rect(center=(modal_x + modal_width // 2, modal_y + 180))
        exit_rect = exit_text.get_rect(center=(modal_x + modal_width // 2, modal_y + 210))
        
        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(restart_text, restart_rect)
        self.screen.blit(exit_text, exit_rect)
    
    def draw_pause(self):
        # 苹果设计规范：绘制暂停界面
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(120)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # 暂停文本
        pause_text = self.title_font.render("游戏暂停", True, LABEL_PRIMARY)
        resume_text = self.body_font.render("按 P 继续游戏", True, LABEL_SECONDARY)
        
        pause_rect = pause_text.get_rect(center=(self.width // 2, self.height // 2 - 20))
        resume_rect = resume_text.get_rect(center=(self.width // 2, self.height // 2 + 20))
        
        self.screen.blit(pause_text, pause_rect)
        self.screen.blit(resume_text, resume_rect)
    
    def reset_game(self):
        self.grid = [[BACKGROUND_SECONDARY for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.get_new_piece()
        self.next_piece = self.get_new_piece()
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_time = 0
        self.fall_speed = 500
        self.paused = False
    
    def run(self):
        game_over = False
        running = True
        
        while running:
            current_time = pygame.time.get_ticks()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if game_over:
                        if event.key == pygame.K_r:
                            self.reset_game()
                            game_over = False
                        elif event.key == pygame.K_ESCAPE:
                            running = False
                    else:
                        if event.key == pygame.K_p:
                            self.paused = not self.paused
                        elif not self.paused:
                            if event.key == pygame.K_LEFT:
                                self.move_piece(-1, 0)
                            elif event.key == pygame.K_RIGHT:
                                self.move_piece(1, 0)
                            elif event.key == pygame.K_DOWN:
                                self.move_piece(0, 1)
                            elif event.key == pygame.K_UP:
                                self.rotate_piece()
                            elif event.key == pygame.K_SPACE:
                                self.hard_drop()
                            elif event.key == pygame.K_ESCAPE:
                                running = False
            
            if not game_over and not self.paused:
                # 自动下降
                if current_time - self.fall_time > self.fall_speed:
                    if not self.drop_piece():
                        game_over = True
                    self.fall_time = current_time
            
            # 绘制游戏
            self.screen.fill(BACKGROUND_PRIMARY)
            self.draw_grid()
            self.draw_piece(self.current_piece)
            self.draw_next_piece()
            self.draw_info()
            
            if game_over:
                self.draw_game_over()
            elif self.paused:
                self.draw_pause()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = TetrisGame()
    game.run()
