import numpy as np
import os
import sys
import yaml
try:
    from psychopy import core, visual, event
except ImportError:
    print("Psychopy not downloaded.")

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base_dir, ".."))

from experiment.triggers import TriggerCode
from stimuli.backend.models import get_gbm_segment, get_btc_segment

config_path = os.path.join(base_dir, "../../config/params.yaml") 

with open(config_path, "r") as f:
     params = yaml.safe_load(f)

class ExperimentAborted(Exception):
    pass

class ExpInterface:
    def __init__(self, fullscr=False):
        self.b_col = "#141E36"
        if fullscr:
            self.win = visual.Window(fullscr=True, color=self.b_col, units="norm")
            self.win_width, self.win_height = self.win.size
        else:
            self.win_width, self.win_height = 800, 600 # Mid-screen = 0,0, x_left = -1
            self.win = visual.Window(size=[self.win_width, self.win_height], fullscr=False, color=self.b_col, units="norm")

        self.fixation_cross = visual.TextStim(text="+", win=self.win, color="white", height=0.2)

        self.default_color = "#3a3f43"

    def fix_cross(self, duration=params["exp"]["iti_duration"]):
        self.fixation_cross.draw()
        self.win.flip()
        keys = event.waitKeys(maxWait=duration, keyList=["escape"])
        if keys and "escape" in keys:
            self.win.close()
            raise ExperimentAborted("Experiment aborted by participant during ITI.")

    def show_instructions(self):
        text = (
            "In this experiment, you will watch live stock market charts.\n"
            "At the start of each trial, you will be told if your starting position is\n"
            "holding an ASSET or holding CASH.\n\n"
            "As you watch the price update on the screen, you can choose to take action:\n"
            "  •  If you hold CASH, press 'B' to BUY the asset.\n"
            "  •  If you hold the ASSET, press 'S' to SELL the asset.\n\n"
            "After the price finishes moving, you will be asked to rate your emotional\n"
            "response to the outcome.\n\n"
            "Your choices matter: At the end of the experiment, one random trial will be\n"
            "drawn. The final value of your portfolio from that specific trial will be\n"
            "paid out to you as a real cash bonus!\n\n"
            "We will begin with 4 practice trials so you can get used to the system.\n"
            "No real money is on the line yet.\n\n"
            "Press the SPACEBAR when you are ready to start practicing."
        )
        stim = visual.TextStim(win=self.win, text=text, pos=(0, 0), color="#FFFFFF",
                               height=0.065, wrapWidth=1.8, alignText="left")
        stim.draw()
        self.win.flip()
        keys = event.waitKeys(keyList=["space", "escape"])
        if "escape" in keys:
            self.win.close()
            raise ExperimentAborted("Experiment aborted by participant during instructions.")

    def show_practice_end(self):
        text = (
            "The practice trials are now over.\n\n"
            "The real experiment is about to begin.\n"
            "From here on, your choices count towards your cash bonus.\n\n"
            "Press the SPACEBAR when you are ready to start."
        )
        stim = visual.TextStim(win=self.win, text=text, pos=(0, 0), color="#FFFFFF",
                               height=0.065, wrapWidth=1.8, alignText="left")
        stim.draw()
        self.win.flip()
        keys = event.waitKeys(keyList=["space", "escape"])
        if "escape" in keys:
            self.win.close()
            raise ExperimentAborted("Experiment aborted by participant during practice end screen.")

    def position_disclosure(self, position, capital, ticker):
        if position == "ASSET":
            text = (f"You own {capital} DKK of this asset: {ticker} \n \n"
                    f"To sell it at any given time, press [{params['exp']['sell_key']}]\n \n"
                    f"To proceed, press Enter")
        else:
            text = (f"You have {capital} DKK in cash. \n \n"
                    f"To buy the asset {ticker} at any given time, press [{params['exp']['buy_key']}]\n \n"
                    f"To proceed, press Enter")
        description = visual.TextStim(win=self.win, text=text, pos=(0, 0), color="#FFFFFF")
        description.draw()
        self.win.flip()
        keys = event.waitKeys(keyList=["return", "escape"])
        if "escape" in keys:
            self.win.close()
            raise ExperimentAborted("Experiment aborted by participant during position disclosure.")
    
    def chart_phase(self, values, position, jump, jump_point, trigger_type):
        # Chart Margins
        margins = {
            "left": -1 + 2*0.1,
            "right": -1 + 2*0.9,
            "bottom": -1 + 2*0.3,
            "up": -1 + 2*0.9
        }

        # X-coordinates and Y-coordinates
        xs = np.linspace(margins["left"], margins["right"], len(values))

        # Static chart frame elements
        axis_colors = self.default_color

        x_axis = visual.Line(self.win, start=(margins["left"], margins["bottom"]), end=(margins["right"], margins["bottom"]),
                     lineColor=axis_colors, lineWidth=6)
        y_axis = visual.Line(self.win, start=(margins["left"], margins["bottom"]), end=(margins["left"], margins["up"]),
                     lineColor=axis_colors, lineWidth=6)
        price_line = visual.ShapeStim(self.win, vertices=[(0, 0), (0, 0)], closeShape=False,
                        lineColor="#2196f3", fillColor=None, lineWidth=5)
        midline = visual.Line(self.win, start=(margins["left"], 0), end=(margins["right"], 0),
                      lineColor="#6a7482", lineWidth=1)
        y_top_text = visual.TextStim(win=self.win, text="",
                                     pos=(margins["left"]-0.05, margins["up"]), height=0.05, color=axis_colors)
        y_bottom_text = visual.TextStim(win=self.win, text="",
                                     pos=(margins["left"]-0.05, margins["bottom"]), height=0.05, color=axis_colors)

        def _recompute_scale(visible_values):
            center = np.mean([np.max(visible_values), np.min(visible_values)])
            half_range = max(center * 0.10, np.ptp(visible_values) * 0.6 + 1e-9)
            return center - half_range, center + half_range

        def portfolio_display(init_value, value, margins, position):
            left_x = margins["left"]+0.3
            right_x = margins["right"] - 0.3
            text_offset_y = margins["bottom"]-0.2
            num_offset_y = margins["bottom"]-0.3

            if value > round(init_value, 2):
                num_color = "green"
            elif value < round(init_value, 2):
                num_color = "red"
            else:
                num_color = self.default_color

            if position == "ASSET":
                asset_label = "Asset Value:"
                cash_label = "What if: Cash Value"

                description_invested = visual.TextStim(win=self.win, text=asset_label,
                                                pos=(left_x, text_offset_y), color="#FFFFFF")

                portfolio = visual.TextStim(win=self.win, text=str(round(value, 2)),
                                                pos=(left_x, num_offset_y), color=num_color)

                cash_description = visual.TextStim(win=self.win, text=cash_label,
                                    pos=(right_x, text_offset_y), color="#FFFFFF")

                cash = visual.TextStim(win=self.win, text=str(round(init_value,2)),
                                    pos=(right_x, num_offset_y), color=self.default_color)

            else:
                cash_label = "Cash Value"
                asset_label = "What if: Asset Value"

                cash_description = visual.TextStim(win=self.win, text=cash_label,
                                    pos=(left_x, text_offset_y), color="#FFFFFF")

                cash = visual.TextStim(win=self.win, text=str(round(init_value,2)),
                                    pos=(left_x, num_offset_y), color=self.default_color)

                description_invested = visual.TextStim(win=self.win, text=asset_label,
                                                pos=(right_x, text_offset_y), color="#FFFFFF")

                portfolio = visual.TextStim(win=self.win, text=str(round(value, 2)),
                                                pos=(right_x, num_offset_y), color=num_color)
                
            return description_invested, portfolio, cash_description, cash

        def _draw_chart_frame(self, x_axis, y_axis, y_top_text, y_bottom_text, midline, price_line, 
                              margins, values, index, position, display_base, portfolio_value):
            
            visible = values[:index] if index > 0 else values[:1]
            bottom_y, top_y = _recompute_scale(visible)

            ys_visible = np.interp(visible, (bottom_y, top_y), (margins["bottom"], margins["up"]))
            y_mid_px = np.interp(values[0], (bottom_y, top_y), (margins["bottom"], margins["up"]))

            y_top_text.text = f"{top_y:.1f}"
            y_bottom_text.text = f"{bottom_y:.1f}"
            midline.start = (margins["left"], y_mid_px)
            midline.end   = (margins["right"], y_mid_px)

            x_axis.draw()
            y_axis.draw()
            y_top_text.draw()
            y_bottom_text.draw()
            midline.draw()
            if price_line is not None and index > 0:
                price_line.vertices = list(zip(xs[:index], ys_visible))
                price_line.draw()
            pv = portfolio_value if portfolio_value is not None else values[index]
            description_invested, portfolio, cash_description, cash = portfolio_display(
                                                                        display_base, pv, margins, position
                                                                        )
            description_invested.draw()
            portfolio.draw()
            cash_description.draw()
            cash.draw()
            self.win.flip()

        
        _draw_chart_frame(self, x_axis, y_axis, y_top_text, 
                          y_bottom_text, midline, None, margins, 
                          values, 0, position, values[0], None
                          )
        core.wait(2.0)

        action_taken = (False, None)
        action_value = None
        for i in range(2, len(values)+1):
            if action_taken[0] and action_taken[1] == "BUY":
                portfolio_value = values[0] * (values[i-1] / action_value)
                display_base = values[0]
            elif action_taken[0]: 
                portfolio_value = values[i-1]
                display_base = action_value
            else:
                portfolio_value = values[i-1]
                display_base = values[0]

            if i-1 == jump_point:
                code = TriggerCode.SPIKE_POSITIVE if jump > 0 else TriggerCode.SPIKE_NEGATIVE
                self.win.callOnFlip(trigger_type.send, code)

            _draw_chart_frame(self, x_axis, y_axis, y_top_text,
                               y_bottom_text, midline, price_line, margins,
                               values, i, position, display_base, portfolio_value)

            escape = event.getKeys(keyList=["escape"])
            if escape:
                self.win.close()
                raise ExperimentAborted("Experiment aborted by participant during chart phase.")

            if position == "ASSET":
                key = event.getKeys(keyList=[params["exp"]["sell_key"]])
                if key and not action_taken[0]:
                    action_value = values[i-1]
                    position = "CASH"
                    action_taken = (True, "SELL")
                    trigger_type.send(TriggerCode.SELL_ACTION)
            else:
                key = event.getKeys(keyList=[params["exp"]["buy_key"]])
                if key and not action_taken[0]:
                    action_value = values[i-1]
                    position = "ASSET"
                    action_taken = (True, "BUY")
                    trigger_type.send(TriggerCode.BUY_ACTION)

            core.wait(1.0) if i == len(values) else core.wait(0.025)
        
        return action_taken, action_value

    def sam_rating(self):
        prompts = [
            ("valence", "On a scale from 1 to 9, how are you feeling about the trial? \n \n"
                        "Press a key from 1-9, where 1 = very negative and 9 = very positive"),
            ("arousal", "On a scale from 1 to 9, how emotionally intense was the trial? \n \n"
                        "Press a key from 1-9, where 1 = very calm and 9 = very excited"),
            ("regret",  "On a scale from 1 to 9, how much do you regret your decision? \n \n"
                        "Press a key from 1-9, where 1 = no regret and 9 = extreme regret"),
        ]

        responses = {}
        for label, prompt in prompts:
            stim = visual.TextStim(win=self.win, text=prompt, pos=(0, 0), color="#FFFFFF")
            stim.draw()
            self.win.flip()
            keys = event.waitKeys(keyList=["1","2","3","4","5","6","7","8","9","escape"])
            if "escape" in keys:
                self.win.close()
                raise ExperimentAborted("Experiment aborted by participant during SAM rating.")
            responses[label] = int(keys[0])
        
        return responses
    
    def stimuli_validation_phase(self, windows, subject_id, init_value=100, n_per_condition=10):
        windows = np.asarray(windows)
        if len(windows) < n_per_condition:
            raise ValueError(
                f"Need at least {n_per_condition} BTC windows, got {len(windows)}."
            )

        # 0 = model (GBM), 1 = data (BTC)
        labels = np.array([0] * n_per_condition + [1] * n_per_condition)
        np.random.shuffle(labels)

        # Intro screen
        intro_text = (
            "REAL OR FAKE?\n\n"
            f"You will see {2 * n_per_condition} price charts.\n"
            "Some are real historical price data. Others are generated by our model.\n\n"
            "After each chart, decide which it was:\n"
            "  •  Press [1] if you think it was REAL\n"
            "  •  Press [0] if you think it was FAKE\n\n"
            "Press SPACE to begin."
        )
        intro = visual.TextStim(win=self.win, text=intro_text, pos=(0, 0), color="#FFFFFF",
                                height=0.065, wrapWidth=1.8, alignText="left")
        intro.draw()
        self.win.flip()
        keys = event.waitKeys(keyList=["space", "escape"])
        if "escape" in keys:
            self.win.close()
            raise ExperimentAborted("Validation phase aborted at intro.")

        results = {"subject_id": subject_id, "response": [], "truth": [], "correct": []}
        used_btc = set()

        margins = {
            "left": -1 + 2*0.1,
            "right": -1 + 2*0.9,
            "bottom": -1 + 2*0.3,
            "up": -1 + 2*0.85,
        }
        axis_colors = self.default_color

        for trial_idx, label in enumerate(labels):
            if label == 0:
                values = get_gbm_segment(init_value=init_value)
                truth = "model"
            else:
                available = [i for i in range(len(windows)) if i not in used_btc]
                chosen = int(np.random.choice(available))
                used_btc.add(chosen)
                values = get_btc_segment([windows[chosen]], init_value=init_value)
                truth = "data"

            xs = np.linspace(margins["left"], margins["right"], len(values))
            x_axis = visual.Line(self.win, start=(margins["left"], margins["bottom"]),
                                 end=(margins["right"], margins["bottom"]),
                                 lineColor=axis_colors, lineWidth=6)
            y_axis = visual.Line(self.win, start=(margins["left"], margins["bottom"]),
                                 end=(margins["left"], margins["up"]),
                                 lineColor=axis_colors, lineWidth=6)
            price_line = visual.ShapeStim(self.win, vertices=[(0, 0), (0, 0)], closeShape=False,
                                          lineColor="#2196f3", fillColor=None, lineWidth=5)
            midline = visual.Line(self.win, start=(margins["left"], 0),
                                  end=(margins["right"], 0), lineColor="#6a7482", lineWidth=1)
            y_top_text = visual.TextStim(win=self.win, text="",
                                         pos=(margins["left"]-0.05, margins["up"]),
                                         height=0.05, color=axis_colors)
            y_bottom_text = visual.TextStim(win=self.win, text="",
                                            pos=(margins["left"]-0.05, margins["bottom"]),
                                            height=0.05, color=axis_colors)
            title = visual.TextStim(win=self.win,
                                    text=f"Chart {trial_idx + 1} of {2 * n_per_condition}",
                                    pos=(0, 0.92), color="#FFFFFF", height=0.07)

            n_frames = len(values)
            tick_wait = max(0.015, 4.5 / max(n_frames - 1, 1))

            def _draw(index):
                visible = values[:index] if index > 0 else values[:1]
                center = np.mean([np.max(visible), np.min(visible)])
                half_range = max(center * 0.10, np.ptp(visible) * 0.6 + 1e-9)
                bottom_y = center - half_range
                top_y = center + half_range
                ys_visible = np.interp(visible, (bottom_y, top_y), (margins["bottom"], margins["up"]))
                y_mid_px = np.interp(values[0], (bottom_y, top_y), (margins["bottom"], margins["up"]))

                y_top_text.text = f"{top_y:.1f}"
                y_bottom_text.text = f"{bottom_y:.1f}"
                midline.start = (margins["left"], y_mid_px)
                midline.end = (margins["right"], y_mid_px)

                title.draw()
                x_axis.draw()
                y_axis.draw()
                y_top_text.draw()
                y_bottom_text.draw()
                midline.draw()
                if index > 0:
                    price_line.vertices = list(zip(xs[:index], ys_visible))
                    price_line.draw()
                self.win.flip()

            _draw(0)
            core.wait(0.3)
            for i in range(2, n_frames + 1):
                _draw(i)
                if event.getKeys(keyList=["escape"]):
                    self.win.close()
                    raise ExperimentAborted("Validation phase aborted during chart.")
                core.wait(tick_wait)
            core.wait(0.4)

            prompt = visual.TextStim(win=self.win,
                                     text="Was that REAL or FAKE?\n\n[1] = REAL      [0] = FAKE",
                                     pos=(0, 0), color="#FFFFFF", height=0.09,
                                     alignText="center")
            prompt.draw()
            self.win.flip()
            keys = event.waitKeys(keyList=["1", "0", "escape"])
            if "escape" in keys:
                self.win.close()
                raise ExperimentAborted("Validation phase aborted at response.")

            response = "real" if keys[0] == "1" else "fake"
            correct = (response == "real" and truth == "data") or \
                      (response == "fake" and truth == "model")

            results["response"].append(response)
            results["truth"].append(truth)
            results["correct"].append(bool(correct))

        return results