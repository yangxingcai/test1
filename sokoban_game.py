import pygame
import sys
import copy

# 初始化pygame
pygame.init()

# 游戏常量
CELL_SIZE = 50
GRID_X_OFFSET = 50
GRID_Y_OFFSET = 80

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
SYSTEM_BROWN = (162, 132, 94)
SYSTEM_GRAY = (142, 142, 147)

# 游戏颜色
FLOOR_COLOR = (245, 245, 247)
WALL_COLOR = (99, 99, 102)
BOX_COLOR = SYSTEM_ORANGE
TARGET_COLOR = SYSTEM_GREEN
PLAYER_COLOR = SYSTEM_BLUE
BOX_ON_TARGET_COLOR = (255, 204, 0)
WHITE = (255, 255, 255)

# 边框和分割线
SEPARATOR = (198, 198, 200)

# 地图元素
WALL = '#'
FLOOR = ' '
BOX = '$'
TARGET = '.'
PLAYER = '@'
BOX_ON_TARGET = '*'
PLAYER_ON_TARGET = '+'

# 方向常量
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class SokobanGame:
    def __init__(self):
        # 关卡设计 - 3个关卡，难度逐渐增加
        self.levels = [
            # 关卡1 - 简单入门（1个箱子）
            [
                "  #####",
                "  #   #",
                "  #$  #",
                "###  .##",
                "#  @   #",
                "#      #",
                "########"
            ],
            # 关卡2 - 中等难度（3个箱子）
            [
                " ########",
                " #      #",
                " # .$. ##",
                "## $@$  #",
                "#  .    #",
                "#       #",
                "#########"
            ],
            # 关卡3 - 困难（4个箱子，需要策略）
            [
                "  #######",
                "  #     #",
                "  # .$. #",
                "### $ $ #",
                "#  .$.  #",
                "#   @   #",
                "#########"
            ]
        ]
        
        self.current_level = 0
        self.load_level(self.current_level)
        
        # 窗口设置
        self.width = 900
        self.height = 700
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("推箱子 - Sokoban")
        self.clock = pygame.time.Clock()
        
        # 游戏状态
        self.moves = 0
        self.pushes = 0
        self.history = []  # 用于撤销功能
        
        # 苹果设计规范字体系统
        try:
            self.title_font = pygame.font.Font(None, 48)
            self.headline_font = pygame.font.Font(None, 32)
            self.body_font = pygame.font.Font(None, 20)
            self.caption_font = pygame.font.Font(None, 16)
        except:
            self.title_font = pygame.font.Font(None, 36)
            self.headline_font = pygame.font.Font(None, 28)
            self.body_font = pygame.font.Font(None, 18)
            self.caption_font = pygame.font.Font(None, 14)
    
    def load_level(self, level_index):
        """加载关卡"""
        if level_index >= len(self.levels):
            return False
        
        self.current_level = level_index
        self.grid = [list(row) for row in self.levels[level_index]]
        self.grid_height = len(self.grid)
        self.grid_width = max(len(row) for row in self.grid)
        
        # 确保所有行长度一致
        for row in self.grid:
            while len(row) < self.grid_width:
                row.append(' ')
        
        # 找到玩家初始位置
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell == PLAYER or cell == PLAYER_ON_TARGET:
                    self.player_pos = [x, y]
                    return True
        return True
    
    def get_cell(self, x, y):
        """获取指定位置的单元格内容"""
        if 0 <= y < len(self.grid) and 0 <= x < len(self.grid[y]):
            return self.grid[y][x]
        return WALL
    
    def set_cell(self, x, y, value):
        """设置指定位置的单元格内容"""
        if 0 <= y < len(self.grid) and 0 <= x < len(self.grid[y]):
            self.grid[y][x] = value
    
    def can_move(self, x, y):
        """检查是否可以移动到指定位置"""
        cell = self.get_cell(x, y)
        return cell in [FLOOR, TARGET]
    
    def is_box(self, x, y):
        """检查指定位置是否有箱子"""
        cell = self.get_cell(x, y)
        return cell in [BOX, BOX_ON_TARGET]
    
    def is_target(self, x, y):
        """检查指定位置是否是目标点"""
        cell = self.get_cell(x, y)
        return cell in [TARGET, BOX_ON_TARGET, PLAYER_ON_TARGET]
    
    def save_state(self):
        """保存当前状态用于撤销"""
        state = {
            'grid': copy.deepcopy(self.grid),
            'player_pos': self.player_pos.copy(),
            'moves': self.moves,
            'pushes': self.pushes
        }
        self.history.append(state)
    
    def undo(self):
        """撤销上一步"""
        if self.history:
            state = self.history.pop()
            self.grid = state['grid']
            self.player_pos = state['player_pos']
            self.moves = state['moves']
            self.pushes = state['pushes']
    
    def move_player(self, direction):
        """移动玩家"""
        new_x = self.player_pos[0] + direction[0]
        new_y = self.player_pos[1] + direction[1]
        
        # 检查是否可以移动
        if self.get_cell(new_x, new_y) == WALL:
            return False
        
        # 保存状态
        self.save_state()
        
        # 检查是否推箱子
        if self.is_box(new_x, new_y):
            box_new_x = new_x + direction[0]
            box_new_y = new_y + direction[1]
            
            # 检查箱子后面是否可以放置
            if not self.can_move(box_new_x, box_new_y):
                self.history.pop()  # 无法移动，移除保存的状态
                return False
            
            # 移动箱子
            box_target = self.is_target(box_new_x, box_new_y)
            self.set_cell(box_new_x, box_new_y, BOX_ON_TARGET if box_target else BOX)
            
            # 更新箱子原位置
            box_was_on_target = self.is_target(new_x, new_y)
            self.set_cell(new_x, new_y, TARGET if box_was_on_target else FLOOR)
            
            self.pushes += 1
        
        # 更新玩家原位置
        player_was_on_target = self.is_target(self.player_pos[0], self.player_pos[1])
        self.set_cell(self.player_pos[0], self.player_pos[1], 
                     TARGET if player_was_on_target else FLOOR)
        
        # 移动玩家
        self.player_pos = [new_x, new_y]
        player_on_target = self.is_target(new_x, new_y)
        self.set_cell(new_x, new_y, PLAYER_ON_TARGET if player_on_target else PLAYER)
        
        self.moves += 1
        return True
    
    def is_level_complete(self):
        """检查关卡是否完成"""
        for row in self.grid:
            for cell in row:
                if cell == BOX:  # 还有箱子不在目标点上
                    return False
        return True
    
    def draw_grid(self):
        """绘制游戏网格"""
        # 计算网格位置使其居中
        grid_pixel_width = self.grid_width * CELL_SIZE
        grid_pixel_height = self.grid_height * CELL_SIZE
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
        pygame.draw.rect(self.screen, SEPARATOR, game_area_rect, 2, border_radius=12)
        
        # 绘制每个单元格
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                rect = pygame.Rect(
                    offset_x + x * CELL_SIZE,
                    offset_y + y * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )
                
                # 绘制地板
                if cell != WALL:
                    pygame.draw.rect(self.screen, FLOOR_COLOR, rect)
                
                # 绘制墙壁
                if cell == WALL:
                    pygame.draw.rect(self.screen, WALL_COLOR, rect, border_radius=4)
                    pygame.draw.rect(self.screen, SEPARATOR, rect, 1, border_radius=4)
                
                # 绘制目标点
                elif cell in [TARGET, PLAYER_ON_TARGET]:
                    inner_rect = pygame.Rect(
                        rect.x + CELL_SIZE // 4,
                        rect.y + CELL_SIZE // 4,
                        CELL_SIZE // 2,
                        CELL_SIZE // 2
                    )
                    pygame.draw.circle(self.screen, TARGET_COLOR, inner_rect.center, CELL_SIZE // 6, 3)
                
                # 绘制箱子
                elif cell == BOX:
                    inner_rect = pygame.Rect(
                        rect.x + 5,
                        rect.y + 5,
                        CELL_SIZE - 10,
                        CELL_SIZE - 10
                    )
                    pygame.draw.rect(self.screen, BOX_COLOR, inner_rect, border_radius=8)
                    pygame.draw.rect(self.screen, WHITE, inner_rect, 2, border_radius=8)
                
                # 绘制在目标点上的箱子
                elif cell == BOX_ON_TARGET:
                    # 先绘制目标点
                    inner_rect = pygame.Rect(
                        rect.x + CELL_SIZE // 4,
                        rect.y + CELL_SIZE // 4,
                        CELL_SIZE // 2,
                        CELL_SIZE // 2
                    )
                    pygame.draw.circle(self.screen, TARGET_COLOR, inner_rect.center, CELL_SIZE // 6, 3)
                    
                    # 再绘制箱子
                    box_rect = pygame.Rect(
                        rect.x + 5,
                        rect.y + 5,
                        CELL_SIZE - 10,
                        CELL_SIZE - 10
                    )
                    pygame.draw.rect(self.screen, SYSTEM_GREEN, box_rect, border_radius=8)
                    pygame.draw.rect(self.screen, WHITE, box_rect, 2, border_radius=8)
                
                # 绘制玩家
                elif cell in [PLAYER, PLAYER_ON_TARGET]:
                    if cell == PLAYER_ON_TARGET:
                        # 先绘制目标点
                        inner_rect = pygame.Rect(
                            rect.x + CELL_SIZE // 4,
                            rect.y + CELL_SIZE // 4,
                            CELL_SIZE // 2,
                            CELL_SIZE // 2
                        )
                        pygame.draw.circle(self.screen, TARGET_COLOR, inner_rect.center, CELL_SIZE // 6, 3)
                    
                    # 绘制玩家
                    player_rect = pygame.Rect(
                        rect.x + 8,
                        rect.y + 8,
                        CELL_SIZE - 16,
                        CELL_SIZE - 16
                    )
                    pygame.draw.circle(self.screen, PLAYER_COLOR, player_rect.center, (CELL_SIZE - 16) // 2)
                    pygame.draw.circle(self.screen, WHITE, player_rect.center, (CELL_SIZE - 16) // 2, 2)
                
                # 绘制网格线
                pygame.draw.rect(self.screen, SEPARATOR, rect, 1)
    
    def draw_header(self):
        """绘制顶部标题栏"""
        # 标题
        title_text = self.title_font.render("推箱子", True, LABEL_PRIMARY)
        title_rect = title_text.get_rect(center=(self.width // 2, 35))
        self.screen.blit(title_text, title_rect)
        
        # 关卡信息
        level_text = self.body_font.render(f"关卡 {self.current_level + 1}/{len(self.levels)}", True, SYSTEM_BLUE)
        level_rect = level_text.get_rect(center=(self.width // 2, 60))
        self.screen.blit(level_text, level_rect)
    
    def draw_info(self):
        """绘制游戏信息"""
        # 信息卡片位置
        info_x = 50
        info_y = self.height - 150
        
        # 统计信息卡片
        stats_card = pygame.Rect(info_x - 10, info_y - 10, 200, 120)
        pygame.draw.rect(self.screen, BACKGROUND_SECONDARY, stats_card, border_radius=12)
        pygame.draw.rect(self.screen, SEPARATOR, stats_card, 1, border_radius=12)
        
        # 统计信息
        moves_text = self.body_font.render(f"移动次数: {self.moves}", True, LABEL_PRIMARY)
        pushes_text = self.body_font.render(f"推动次数: {self.pushes}", True, LABEL_PRIMARY)
        
        self.screen.blit(moves_text, (info_x, info_y))
        self.screen.blit(pushes_text, (info_x, info_y + 30))
        
        # 控制说明卡片
        controls_x = self.width - 250
        controls_y = self.height - 200
        controls_card = pygame.Rect(controls_x - 10, controls_y - 10, 240, 180)
        pygame.draw.rect(self.screen, BACKGROUND_SECONDARY, controls_card, border_radius=12)
        pygame.draw.rect(self.screen, SEPARATOR, controls_card, 1, border_radius=12)
        
        controls_title = self.headline_font.render("控制", True, LABEL_PRIMARY)
        title_rect = controls_title.get_rect(center=(controls_x + 110, controls_y + 10))
        self.screen.blit(controls_title, title_rect)
        
        controls = [
            ("↑ ↓ ← →", "移动"),
            ("U", "撤销"),
            ("R", "重新开始"),
            ("N", "下一关"),
            ("ESC", "退出")
        ]
        
        for i, (key, desc) in enumerate(controls):
            key_text = self.body_font.render(key, True, SYSTEM_BLUE)
            desc_text = self.caption_font.render(desc, True, LABEL_SECONDARY)
            self.screen.blit(key_text, (controls_x, controls_y + 35 + i * 25))
            self.screen.blit(desc_text, (controls_x, controls_y + 35 + i * 25 + 20))
    
    def draw_level_complete(self):
        """绘制关卡完成界面"""
        # 苹果设计规范：绘制完成模态框
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
        pygame.draw.rect(self.screen, SEPARATOR, modal_rect, 2, border_radius=20)
        
        # 完成文本
        complete_text = self.title_font.render("关卡完成！", True, SYSTEM_GREEN)
        moves_text = self.headline_font.render(f"移动: {self.moves}", True, LABEL_PRIMARY)
        pushes_text = self.headline_font.render(f"推动: {self.pushes}", True, LABEL_PRIMARY)
        
        if self.current_level < len(self.levels) - 1:
            next_text = self.body_font.render("按 N 进入下一关", True, LABEL_SECONDARY)
        else:
            next_text = self.body_font.render("恭喜通关！", True, SYSTEM_BLUE)
        
        restart_text = self.body_font.render("按 R 重新开始", True, LABEL_SECONDARY)
        
        complete_rect = complete_text.get_rect(center=(modal_x + modal_width // 2, modal_y + 60))
        moves_rect = moves_text.get_rect(center=(modal_x + modal_width // 2, modal_y + 110))
        pushes_rect = pushes_text.get_rect(center=(modal_x + modal_width // 2, modal_y + 150))
        next_rect = next_text.get_rect(center=(modal_x + modal_width // 2, modal_y + 200))
        restart_rect = restart_text.get_rect(center=(modal_x + modal_width // 2, modal_y + 230))
        
        self.screen.blit(complete_text, complete_rect)
        self.screen.blit(moves_text, moves_rect)
        self.screen.blit(pushes_text, pushes_rect)
        self.screen.blit(next_text, next_rect)
        self.screen.blit(restart_text, restart_rect)
    
    def reset_level(self):
        """重置当前关卡"""
        self.load_level(self.current_level)
        self.moves = 0
        self.pushes = 0
        self.history = []
    
    def next_level(self):
        """进入下一关"""
        if self.current_level < len(self.levels) - 1:
            self.current_level += 1
            self.load_level(self.current_level)
            self.moves = 0
            self.pushes = 0
            self.history = []
            return True
        return False
    
    def run(self):
        """运行游戏主循环"""
        running = True
        level_complete = False
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if level_complete:
                        if event.key == pygame.K_n:
                            if self.next_level():
                                level_complete = False
                        elif event.key == pygame.K_r:
                            self.reset_level()
                            level_complete = False
                        elif event.key == pygame.K_ESCAPE:
                            running = False
                    else:
                        if event.key == pygame.K_UP:
                            self.move_player(UP)
                        elif event.key == pygame.K_DOWN:
                            self.move_player(DOWN)
                        elif event.key == pygame.K_LEFT:
                            self.move_player(LEFT)
                        elif event.key == pygame.K_RIGHT:
                            self.move_player(RIGHT)
                        elif event.key == pygame.K_u:
                            self.undo()
                        elif event.key == pygame.K_r:
                            self.reset_level()
                        elif event.key == pygame.K_n:
                            if self.next_level():
                                level_complete = False
                        elif event.key == pygame.K_ESCAPE:
                            running = False
                        
                        # 检查是否完成关卡
                        if self.is_level_complete():
                            level_complete = True
            
            # 绘制游戏
            self.screen.fill(BACKGROUND_PRIMARY)
            self.draw_header()
            self.draw_grid()
            self.draw_info()
            
            if level_complete:
                self.draw_level_complete()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = SokobanGame()
    game.run()

