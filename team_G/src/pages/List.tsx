import React, { useState } from "react";
import styled from "styled-components";
import Post from "../components/Post";

function List() {
  const [parm, setParm] = useState("");
  const [image, setImage] = useState<File | null>(null);
  const [posts, setPosts] = useState([]);

  //api 들어갈곳

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedImage = e.target.files && e.target.files[0];
    setImage(selectedImage);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (parm) {
      const newPost = { parm, image };
      //api 들어갈곳
      setPosts([...posts, newPost]);
      setParm("");
      setImage(null);
    }
  };

  return (
    <>
      <NewPostForm onSubmit={handleSubmit}>
        <Input
          type="text"
          placeholder="파라미터"
          value={parm}
          onChange={(e) => setParm(e.target.value)}
        />
        <ImageInput type="file" accept="image/*" onChange={handleImageChange} />
        <Button type="submit">게시물 추가</Button>
      </NewPostForm>
      <PostListContainer>
        {posts.map((post, index) => (
          <Post key={index} parm={post.parm} image={post.image} />
        ))}
      </PostListContainer>
    </>
  );
}

export default List;

const PostListContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-gap: 16px;
`;

const NewPostForm = styled.form`
  display: flex;
  flex-direction: column;
  margin-bottom: 16px;
`;

const Input = styled.input`
  margin-bottom: 8px;
  padding: 8px;
`;

const ImageInput = styled.input`
  margin-bottom: 8px;
`;

const Button = styled.button`
  padding: 8px;
`;
