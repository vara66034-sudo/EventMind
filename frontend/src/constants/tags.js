export const AVAILABLE_TAGS = [
  'Концерты', 'Театр', 'Выставки', 'Спорт', 'Образование',
  'Музыка', 'Искусство', 'Технологии', 'Бизнес', 'Путешествия',
  'Кулинария', 'Фотография', 'Кино', 'Литература', 'Игры',
  'Наука', 'Мода', 'Здоровье', 'Йога', 'Танцы',
];

export const isValidTag = (tag) => AVAILABLE_TAGS.includes(tag);

export const filterValidTags = (tags) => 
  tags.filter((tag) => isValidTag(tag));
