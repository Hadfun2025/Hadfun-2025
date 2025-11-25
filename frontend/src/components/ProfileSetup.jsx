import { useState } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export function ProfileSetup({ open, onClose, user, onProfileCompleted }) {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    full_name: '',
    birthdate: '',
    bio: '',
    location: '',
    favorite_team: '',
    interests: ''
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const calculateAge = (birthdate) => {
    const today = new Date();
    const birth = new Date(birthdate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    return age;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate required fields
    if (!formData.full_name.trim()) {
      toast.error('Please enter your full name');
      return;
    }

    if (!formData.birthdate) {
      toast.error('Please enter your birthdate');
      return;
    }

    // Check age
    const age = calculateAge(formData.birthdate);
    if (age < 13) {
      toast.error('You must be at least 13 years old to use this platform');
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post(
        `${API}/users/${user.id}/complete-profile`,
        formData
      );

      toast.success('Profile completed! You can now create posts and join the community.');
      onProfileCompleted(response.data);
      onClose();
    } catch (error) {
      console.error('Profile completion error:', error);
      toast.error(error.response?.data?.detail || 'Failed to complete profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && !loading && onClose()}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl">Complete Your Profile</DialogTitle>
          <DialogDescription>
            Welcome to Football With Purpose! Please complete your profile to join our community and start sharing your stories.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 mt-4">
          {/* Full Name - Required */}
          <div className="space-y-2">
            <Label htmlFor="full_name" className="required">
              Full Name <span className="text-red-500">*</span>
            </Label>
            <Input
              id="full_name"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              placeholder="Enter your full name"
              required
              maxLength={100}
            />
          </div>

          {/* Birthdate - Required */}
          <div className="space-y-2">
            <Label htmlFor="birthdate">
              Birthdate <span className="text-red-500">*</span>
            </Label>
            <Input
              id="birthdate"
              name="birthdate"
              type="date"
              value={formData.birthdate}
              onChange={handleChange}
              required
              max={new Date().toISOString().split('T')[0]}
            />
            <p className="text-xs text-gray-500">You must be at least 13 years old</p>
          </div>

          {/* Bio - Optional */}
          <div className="space-y-2">
            <Label htmlFor="bio">About You</Label>
            <Textarea
              id="bio"
              name="bio"
              value={formData.bio}
              onChange={handleChange}
              placeholder="Tell us a bit about yourself and your passion for football..."
              rows={4}
              maxLength={500}
            />
            <p className="text-xs text-gray-500 text-right">
              {formData.bio.length}/500 characters
            </p>
          </div>

          {/* Location - Optional */}
          <div className="space-y-2">
            <Label htmlFor="location">Location</Label>
            <Input
              id="location"
              name="location"
              value={formData.location}
              onChange={handleChange}
              placeholder="e.g., London, UK"
              maxLength={100}
            />
          </div>

          {/* Favorite Team - Optional */}
          <div className="space-y-2">
            <Label htmlFor="favorite_team">Favorite Team</Label>
            <Input
              id="favorite_team"
              name="favorite_team"
              value={formData.favorite_team}
              onChange={handleChange}
              placeholder="e.g., Arsenal, Manchester United"
              maxLength={100}
            />
          </div>

          {/* Interests - Optional */}
          <div className="space-y-2">
            <Label htmlFor="interests">Interests</Label>
            <Input
              id="interests"
              name="interests"
              value={formData.interests}
              onChange={handleChange}
              placeholder="e.g., Charity work, Community football, Youth coaching"
              maxLength={200}
            />
          </div>

          {/* Submit Button */}
          <div className="flex gap-3 pt-4">
            <Button
              type="submit"
              disabled={loading}
              className="flex-1"
            >
              {loading ? 'Completing...' : 'Complete Profile'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
