# Production Pipeline Submissions

## How to Submit Projects

1. **Create a project file**: Place your project description in a `.md` or `.txt` file in this folder
2. **Add instructions** (optional): Create an `instructions.json` file with the same base name
3. **The system will automatically detect and process** new submissions

## File Structure Examples

### Simple Submission

```text
my_project.md           # Project description
```

### Advanced Submission

```text
my_project.md           # Project description
my_project.json         # Instructions and configuration
```

## Instructions File Format

```json
{
  "priority": "high|medium|low",
  "agent_types": ["data_processing", "content_generation", "automation"],
  "deployment_target": "local|cloud|hybrid",
  "requirements": {
    "programming_languages": ["python", "javascript"],
    "frameworks": ["flask", "react"],
    "dependencies": ["pandas", "numpy"]
  },
  "custom_instructions": "Any specific build instructions or requirements"
}
```

## Project File Format

Your project `.md` or `.txt` file should include:

1. **Project Title** (as heading)
2. **Description** - What the project does
3. **Requirements** - Technical requirements
4. **Features** - Key features to implement
5. **Success Criteria** - How to know it's complete

## Status

- Place files here and they will be automatically picked up
- Check `../production.log` for processing status
- Completed projects will be moved to `../projects/`
