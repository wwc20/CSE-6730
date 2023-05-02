import numpy as np
import random
import matplotlib.pyplot as plt

#gamma is the discount factor
gamma = 0.9

#the maximum error allowed in the utility of any state
epsilon = 0.001

class Vehicle:
    def __init__(self, id, lane, exit_lane, v=0):
        self.id = id
        self.lane = lane
        self.exit_lane = exit_lane
        self.v = v

class MDP:
    def __init__(self, vehicle, num_lanes, time_steps, v_min, v_max, points):
        self.vehicle = vehicle
        self.num_lanes = num_lanes
        self.time_steps = time_steps
        self.v_min = v_min
        self.v_max = v_max
        self.transition = self.generate_transition(points)
        self.states = self.transition.keys()

    def generate_transition(self, points):
        trans = {}

        if self.vehicle.id == 0:
            safety_distance = 5
        else:
            safety_distance = 30

        not_safety_range = []
        for i in range(self.v_max * self.time_steps + 1):
            for j in range(self.num_lanes):
                for point in points:
                    if abs(i - point[0]) <= safety_distance and point[1] == j:
                        not_safety_range.append((i, j))
        #print("not safe: ", not_safety_range)
        for sl in range(self.v_max * self.time_steps + 1):
            for si in range(self.num_lanes):
                for sl1 in range(self.v_max * self.time_steps + 1):
                    for si1 in range(self.num_lanes):
                        if (sl, si) and (sl1, si1) not in not_safety_range:
                            if abs(si1 - si) <= 1:
                                next_v = sl1 - sl
                                if self.v_min <= next_v <= self.v_max:
                                    if (sl, si) in trans:
                                        trans[(sl, si)][(sl1 - sl, si1 - si)] = (sl1, si1)
                                    else:
                                        trans[(sl, si)] = {(sl1 - sl, si1 - si): (sl1, si1)}

        #print(trans)
        return trans

    def T(self, state, action):
        """for a state and an action, return a list of (probability, result-state) pairs."""
        return self.transition[state][action]

    def actions(self, state):
        """return set of actions that can be performed in this state"""
        return self.transition[state].keys()

    def reward(self, vehicle, state):
        return state[0] - abs(state[1] - vehicle.exit_lane) * state[0] * 0.5

    def value_iteration(self, vehicle):
        """
        Solving the MDP by value iteration.
        returns utility values for states after convergence
        """
        states = self.states  # v_max * time_steps, num_lanes
        actions = self.actions  # v_max - v_min, 3

        # initialize value of all the states to 0
        utility = {s: 0 for s in states}
        while True:
            new_utility = utility.copy()
            delta = 0

            for s in states:
                utility[s] = self.reward(vehicle, s) + gamma * max([new_utility[self.T(s, a)] for a in actions(s)])
                # calculate maximum difference in value
                delta = max(delta, abs(utility[s] - new_utility[s]))

            # check for convergence, if values converged then return V
            if delta < epsilon * (1 - gamma) / gamma:
                return new_utility

    def best_policy(self, V):
        states = self.states
        actions = self.actions
        pi = {}
        for s in states:
            pi[s] = max(actions(s), key=lambda a: self.expected_utility(a, s, V))
        return pi

    def expected_utility(self, a, s, V):
        return V[self.T(s, a)]

def generate_int_coordinates(num_lanes, num_points, time_steps, v_min, v_max):
    points = []
    while len(points) < num_points:
        l = random.randrange(0, (v_max * time_steps + 1), v_max)
        i = random.randint(0, num_lanes - 1)
        points.append((l, i))
    print("points: ", points)
    return points

def main():
    num_vehicles = 5
    num_lanes = 3
    time_steps = 20
    v_min = 0
    v_max = 10

    vehicles = []
    # for i in range(0, num_vehicles):
    #     initial_lane = random.randint(0, num_lanes - 1)
    #     final_lane = random.randint(0, num_lanes - 1)
    #     for j in range(2):
    #         vehicles.append(Vehicle(j, initial_lane, final_lane))
    vehicles = [Vehicle(0, 0, 1), Vehicle(1, 0, 1), Vehicle(0, 0, 2), Vehicle(1, 0, 2), Vehicle(0, 1, 2), Vehicle(1, 1, 2), Vehicle(0, 0, 0), Vehicle(1, 0, 0), Vehicle(0, 2, 1), Vehicle(1, 2, 1)]
    #points = generate_int_coordinates(num_lanes, 5, time_steps, v_min, v_max)
    points1 = [(10, 1), (40, 2), (60, 1), (150, 2), (200, 1)]
    points2 = [(16, 1), (55, 2), (75, 0), (110, 1), (160, 1)]
    points3 = [(24, 2), (30, 2), (68, 0), (80, 1), (170, 2)]
    situation = [points1, points2, points3]

    x_labels = []
    for vehicle in vehicles:
        print(vehicle.id, vehicle.lane, vehicle.exit_lane)
        if (vehicle.lane, vehicle.exit_lane) not in x_labels:
            x_labels.append((vehicle.lane, vehicle.exit_lane))
    delta_y = np.zeros(num_vehicles)
    for points in situation:


        y0 = []
        y1 = []
        for vehicle in vehicles:
            print(vehicle.id, vehicle.lane, vehicle.exit_lane)
            mdp = MDP(vehicle, num_lanes, time_steps, v_min, v_max, points)
            V = mdp.value_iteration(vehicle)
            # print('State - Value')
            # for s in V:
            #     print(s, ' - ', V[s])
            pi = mdp.best_policy(V)
            # print('\nOptimal policy is \nState - Action')
            # for s in pi:
            #     print(s, ' - ', pi[s])
            trace = []

            if (0, vehicle.lane) in pi:
                trace.append((0, vehicle.lane))
                for t in range(0, time_steps):
                    next_l = trace[t][0] + pi[trace[t]][0]
                    next_i = trace[t][1] + pi[trace[t]][1]
                    if (next_l, next_i) in pi:
                        trace.append((next_l, next_i))
                        if t == time_steps - 1:
                            print("The final position is: ", next_l)
                            print("The final lane is: ", next_i)
                            if vehicle.id == 0:
                                y0.append(next_l)
                            else:
                                y1.append(next_l)
                    else:
                        print("error!")
                        break
            else:
                print("error!")

            print(trace)
        total_width, n = 0.8, 2
        width = total_width / n
        x = np.arange(num_vehicles)
        x = x - (total_width - width) / 2

        plt.bar(x, y0, width=width, label='Autonomous Vehicle')
        plt.bar(x + width, y1, width=width, label='Human Driven Vehicle')
        plt.legend()

        # Set x-axis label
        plt.xlabel('Vehicle (Initial Lane, Target Lane)')

        # Set y-axis label
        plt.ylabel('Final Position (m)')

        # x_lables
        plt.xticks(x + width / 2, x_labels)
        plt.show()
        result = [(y0[i] - y1[i]) / y1[i] * 100 for i in range(len(y1))]
        delta_y = np.add(delta_y, result)

    for i in range(len(delta_y)):
        delta_y[i] = delta_y[i] / 3
    print(delta_y)
    x = np.arange(num_vehicles)

    plt.bar(x, delta_y)

    # Set x-axis label
    plt.xlabel('Vehicle (Initial Lane, Target Lane)')

    # Set y-axis label
    plt.ylabel('Average Percentage Increase (%)')

    # x_lables
    plt.xticks(x, x_labels)
    plt.show()


if __name__ == "__main__":
    main()
