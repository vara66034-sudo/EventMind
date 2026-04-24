export const AVAILABLE_TAGS = [
  'Backend',
  'Frontend',
  'ML',
  'AI',
  'Data Science',
  'DevOps',
  'Mobile',
  'CyberSecurity',
  'Конференция',
  'Митап',
  'Хакатон',
  'Воркшоп',
  'IT',
];

export const isValidTag = (tag) => AVAILABLE_TAGS.includes(tag);

export const filterValidTags = (tags) => 
  tags.filter((tag) => isValidTag(tag));
