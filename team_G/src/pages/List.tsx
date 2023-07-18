import React, { useState, useEffect } from "react";
import styled from "styled-components";
import Post from "../components/Post";

interface Post {
  parm: string;
  image: File | string | null;
}

interface SentencesResponse {
  data: {
    result: string;
    sentence: string;
    processing_time: number;
  }[];
}

function List() {
  const [parm, setParm] = useState("");
  const [image, setImage] = useState<File | null>(null);
  const [posts, setPosts] = useState<Post[]>([]);

  useEffect(() => {
    fetchSentences(); // 컴포넌트가 처음 렌더링될 때 문장 목록을 가져오는 함수 호출
  }, []);

  const delay = (ms: number): Promise<void> => {
    return new Promise((resolve) => {
      setTimeout(resolve, ms);
    });
  }

  // setPosts
  const fetchSentences = async () => {
    try {
      const response = await fetch('/sentences'); // GET 요청으로 문장 목록을 가져오기 위해 /sentences 엔드포인트에 요청
      const data: SentencesResponse = await response.json(); // 서버에서 받은 응답 데이터를 파싱하여 객체로 변환

      setPosts(data.data.map((item) => ({ parm: `${item.sentence} ${item.processing_time}s`, image: item.result }))); // 받은 문장 목록을 Post 객체의 배열로 변환하여 상태에 설정하여 화면에 표시

    } catch (error) {
      console.error('Error fetching sentences:', error);
    }
  };

  const getTaskResult = async (taskId: string) => {
    while (true) {
      const response = await fetch(`/sentences/${taskId}`);

      if (response.status === 200) {
        const data = await response.json();
        const result = data.result;
        if (result !== null) {
          console.log(`img created in ${data.processing_time}s ${result}`)

          return { result: result, processing_time: data.processing_time };
        }
      } else if (response.status === 202) {
        // await delay(1000); // 1초 대기 후 재요청
      } else if (response.status === 404) {
        throw new Error('Task not found');
      } else if (response.status === 500) {
        throw new Error('Task failed to complete');
      }
    }
  }

  const saveSentence = async () => {
    const newPost = { parm, image };

    try {
      const response = await fetch('/sentences', { // POST 요청으로 새로운 문장을 저장하기 위해 /sentences 엔드포인트에 요청
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ sentence: parm }), // 요청의 본문에 새로운 문장을 담아 전송
      });

      if (response.ok) { // 요청이 성공적으로 완료되었다면
        const index = posts.length

        setPosts([...posts, newPost]);
        setParm("");
        setImage(null);

        response.json().then(async (responseData) => {
          console.log(responseData);

          await delay(1000);

          const data = await getTaskResult(responseData.task_id)

          setPosts((prevPosts) => {
            const updatedPosts = [...prevPosts];
            const updatedPost = { ...prevPosts[index], parm: `${newPost.parm} ${data.processing_time}s`, image: data.result }; // 업데이트할 내용 적용
            updatedPosts[index] = updatedPost;
            return updatedPosts;
          });
        });
      } else {
        console.error('Error saving sentence_r:', response.statusText);
      }
    } catch (error) {
      console.error('Error saving sentence_f:', error);
    }
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedImage = e.target.files && e.target.files[0];
    setImage(selectedImage);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (parm && parm.trim() !== '') {
      saveSentence();
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
