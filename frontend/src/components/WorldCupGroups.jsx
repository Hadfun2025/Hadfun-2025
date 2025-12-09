import { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export function WorldCupGroups() {
  const [groups, setGroups] = useState([]);
  const [fixtures, setFixtures] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadWorldCupData();
  }, []);

  const loadWorldCupData = async () => {
    try {
      setLoading(true);
      
      // Load groups
      const groupsRes = await axios.get(`${API}/world-cup/groups`);
      setGroups(groupsRes.data);
      
      // Load fixtures
      const fixturesRes = await axios.get(`${API}/fixtures?league_ids=1&days_ahead=365`);
      setFixtures(fixturesRes.data);
      
    } catch (error) {
      console.error('Error loading World Cup data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-lg">Loading World Cup 2026...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-8 rounded-lg">
        <h1 className="text-4xl font-bold mb-2">🏆 FIFA World Cup 2026</h1>
        <p className="text-xl">USA • Canada • Mexico</p>
        <p className="text-lg opacity-90 mt-2">June 11 - July 19, 2026</p>
      </div>

      {/* Group Stage Info */}
      <Card>
        <CardHeader>
          <CardTitle>Tournament Format</CardTitle>
          <CardDescription>48 teams, 12 groups of 4 teams each</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-600">
            Top 2 teams from each group advance to the Round of 32. 
            The tournament features {fixtures.length} total matches across three host nations.
          </p>
        </CardContent>
      </Card>

      {/* Groups Display */}
      <div>
        <h2 className="text-2xl font-bold mb-4">Group Stage Draw</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {groups.map((group) => (
            <Card key={group.group_name} className="hover:shadow-lg transition-shadow">
              <CardHeader className="bg-gradient-to-r from-blue-50 to-purple-50 pb-3">
                <CardTitle className="text-center text-xl">
                  Group {group.group_name}
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-4">
                <div className="space-y-2">
                  {group.teams.map((team, idx) => (
                    <div 
                      key={idx}
                      className="flex items-center p-2 rounded hover:bg-gray-50 transition-colors"
                    >
                      <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3">
                        {idx + 1}
                      </div>
                      <span className="font-medium text-sm">{team}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Fixtures Info */}
      {fixtures.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Matches Available</CardTitle>
            <CardDescription>
              All World Cup 2026 matches are now available for predictions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <Badge variant="secondary" className="text-lg px-4 py-2">
                {fixtures.length} Matches
              </Badge>
              <span className="text-sm text-gray-600">
                Navigate to the Fixtures tab and select "World Cup" to make your predictions!
              </span>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
