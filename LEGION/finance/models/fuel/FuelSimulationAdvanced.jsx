
import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

export default function FuelSimulationAdvanced() {
  const [time, setTime] = useState(0);
  const [entropyPool, setEntropyPool] = useState([]);
  const [priceHistory, setPriceHistory] = useState([]);
  const [agents, setAgents] = useState([]);
  const [running, setRunning] = useState(false);
  const [bondingRate, setBondingRate] = useState(0.05);
  const [governanceVotes, setGovernanceVotes] = useState([]);

  const roles = ['stabilizer', 'speculator', 'archivist', 'igniter'];

  useEffect(() => {
    const initialAgents = Array.from({ length: 100 }, (_, id) => {
      const role = roles[Math.floor(Math.random() * roles.length)];
      return { id, role, fuel: 100, bonded: 0, decayed: 0, entropyClaimed: 0, reputation: 0 };
    });
    setAgents(initialAgents);
  }, []);

  useEffect(() => {
    if (!running) return;
    const interval = setInterval(() => {
      simulateStep();
    }, 500);
    return () => clearInterval(interval);
  }, [running, time]);

  const decayRate = (role) => {
    switch (role) {
      case 'stabilizer': return 0.008;
      case 'speculator': return 0.012;
      case 'archivist': return 0.01;
      default: return 0.015;
    }
  };

  const simulateStep = () => {
    let entropy = 0;
    const updatedAgents = agents.map(agent => {
      const decay = agent.fuel * decayRate(agent.role);
      const claim = agent.role === 'stabilizer' ? decay * 0.4 : 0;
      const bondGain = agent.bonded > 0 ? agent.bonded * bondingRate : 0;
      const newFuel = Math.max(agent.fuel - decay + claim + bondGain, 0);
      const newRep = agent.reputation + (claim > 0 ? 1 : 0);

      let newRole = agent.role;
      if (newRep > 10 && agent.role === 'speculator') newRole = 'stabilizer';
      if (agent.decayed > 100 && agent.role !== 'archivist') newRole = 'archivist';

      entropy += decay;
      return {
        ...agent,
        fuel: newFuel,
        bonded: agent.bonded,
        decayed: agent.decayed + decay,
        entropyClaimed: agent.entropyClaimed + claim,
        reputation: newRep,
        role: newRole
      };
    });

    if (time % 20 === 0) {
      const averageEntropy = entropy / agents.length;
      const proposal = {
        time,
        newBondingRate: bondingRate + (averageEntropy > 1 ? 0.005 : -0.0025)
      };
      setGovernanceVotes(prev => [...prev, proposal]);
      setBondingRate(proposal.newBondingRate);
    }

    setAgents(updatedAgents);
    setEntropyPool(prev => [...prev, { time, entropy: entropy.toFixed(2) }]);
    setPriceHistory(prev => [...prev, { time, price: (100 + Math.sin(time / 4) * 8 + Math.random() * 3).toFixed(2) }]);
    setTime(prev => prev + 1);
  };

  const bondAllAgents = () => {
    const bondedAgents = agents.map(agent => ({
      ...agent,
      bonded: agent.fuel * 0.3,
      fuel: agent.fuel * 0.7
    }));
    setAgents(bondedAgents);
  };

  return (
    <div className="p-6 grid grid-cols-1 gap-6 bg-[#e0e5ec] min-h-screen text-gray-800">
      <div className="flex items-center gap-6">
        <Button onClick={() => setRunning(!running)} className="shadow-neumorphic">
          {running ? 'Pause' : 'Start'} Simulation
        </Button>
        <Button onClick={bondAllAgents} className="shadow-neumorphic">
          Bond 30% of Each Agent
        </Button>
        <div className="text-sm">Time: {time}</div>
      </div>

      <Card className="shadow-neumorphic rounded-xl">
        <CardContent>
          <h2 className="text-xl font-semibold mb-4">Entropy Pool</h2>
          <LineChart width={600} height={250} data={entropyPool}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="entropy" stroke="#8884d8" name="Entropy" />
          </LineChart>
        </CardContent>
      </Card>

      <Card className="shadow-neumorphic rounded-xl">
        <CardContent>
          <h2 className="text-xl font-semibold mb-4">Quantum Price History</h2>
          <LineChart width={600} height={250} data={priceHistory}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="price" stroke="#82ca9d" name="Price" />
          </LineChart>
        </CardContent>
      </Card>

      <Card className="shadow-neumorphic rounded-xl">
        <CardContent>
          <h2 className="text-xl font-semibold mb-4">Governance Votes</h2>
          <ul className="text-sm space-y-1">
            {governanceVotes.slice(-5).map(vote => (
              <li key={vote.time}>
                t={vote.time}: bonding rate changed to {vote.newBondingRate.toFixed(4)}
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
